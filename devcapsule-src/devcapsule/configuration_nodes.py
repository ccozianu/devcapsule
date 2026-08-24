"""The configuration-node registry: one canonical name for every node.

*Every Node Has One Name* (see
``engineering-docs/design-notes/devcapsule/v1-user-experience.md``): every
node in the configuration tree that can need user input is addressable on the
command line by the same canonical name everywhere it appears — the ``config``
family, the ``init``/``run`` carrier options, and the interactive prompt all
spell it identically.  This module is the single authority for that
vocabulary.  Adding a component, capability, or host boundary adds *rows*
here, never new command-line syntax.

Node names come from the project's own declarations, so the registry is built
per project from the manifest and platform lock rather than hard-coded:

- ``set`` nodes are the manifest's declared configuration values;
- ``bind`` nodes are the locked components' state slots (``host-directory``
  provider) and secret inputs (``host-environment`` provider), spelled as
  ``provider:value`` in the bind grammar;
- ``authorize`` nodes are the security-tier declarations derived from the
  manifest's host recommendations and the lock's base and component
  acquisitions.

Uniqueness is enforced by construction: building a registry whose sources
declare the same name twice fails loudly, because a name that means two
things would make ``--set``/``--bind``/``--authorize``, ``unset``, and the
prompt ambiguous.

This module owns *naming and addressing* only.  Value validation and artifact
writes stay with the operation layer, which reaches the underlying
declaration through :attr:`ConfigurationNode.declaration`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from devcapsule.project_configuration import (
    CURATED_HOST_RECOMMENDATIONS,
    ProjectConfigurationError,
    authorization_declarations,
    component_secret_inputs,
    configuration_binding_declarations,
    configuration_value_declarations,
)

__all__ = [
    "CARRIER_FAMILY_AUTHORIZE",
    "CARRIER_FAMILY_BIND",
    "CARRIER_FAMILY_SET",
    "ConfigurationNode",
    "NodeRegistry",
    "PROVIDER_HOST_DIRECTORY",
    "PROVIDER_HOST_ENVIRONMENT",
    "build_node_registry",
]


CARRIER_FAMILY_SET = "set"
CARRIER_FAMILY_BIND = "bind"
CARRIER_FAMILY_AUTHORIZE = "authorize"

# Bind-family provider names deliberately match the checkout-record table
# names (``configuration.bindings.host-directory`` / ``.host-environment``),
# so the value a user types is the vocabulary the artifact records.
PROVIDER_HOST_DIRECTORY = "host-directory"
PROVIDER_HOST_ENVIRONMENT = "host-environment"


@dataclass(frozen=True)
class ConfigurationNode:
    """One named node of the configuration tree.

    ``declaration`` carries the source metadata the operation layer validates
    against (a manifest value declaration, a component state slot or secret
    input, or an :class:`AuthorizationDeclaration`); the registry itself never
    interprets it.
    """

    name: str
    family: str
    description: str
    # Whether resolution fails while this node is unanswered.  Recommended
    # authorizations are deliberately not required: denial is the consumer's
    # default and declining is an answer.
    required: bool
    declaration: Any
    # bind-family only: the providers this node's value may name.
    providers: tuple[str, ...] = ()
    # authorize-family only: whether an owner authoring this node's project
    # recommendation must attach a justification (the curated host boundaries).
    accepts_justification: bool = False


class NodeRegistry:
    """All configuration nodes of one project/lock pair, keyed by name."""

    def __init__(self, nodes: Iterable[ConfigurationNode]) -> None:
        self._nodes: dict[str, ConfigurationNode] = {}
        for node in nodes:
            existing = self._nodes.get(node.name)
            if existing is not None:
                raise ProjectConfigurationError(
                    f"Configuration node {node.name!r} is declared twice, as a "
                    f"{existing.family!r} node and as a {node.family!r} node; every node "
                    "in the configuration tree has exactly one name."
                )
            self._nodes[node.name] = node

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._nodes))

    def get(self, name: str) -> ConfigurationNode | None:
        return self._nodes.get(name)

    def node(self, name: str) -> ConfigurationNode:
        found = self._nodes.get(name)
        if found is None:
            available = ", ".join(self.names()) or "none"
            raise ProjectConfigurationError(
                f"Configuration node {name!r} is not declared by this project and lock; "
                f"declared nodes: {available}."
            )
        return found

    def family(self, family: str) -> tuple[ConfigurationNode, ...]:
        return tuple(
            node for _, node in sorted(self._nodes.items()) if node.family == family
        )

    def answerable(self, name: str, family: str) -> ConfigurationNode:
        """Return the node when the given carrier family may answer it.

        A valid name answered through the wrong carrier is a distinct mistake
        from an unknown name, and the message must say which spelling is
        right rather than deny the node exists.
        """

        node = self.node(name)
        if node.family != family:
            raise ProjectConfigurationError(
                f"Configuration node {name!r} is answered with "
                f"--{node.family}, not --{family}."
            )
        return node

    def split_bind_value(self, name: str, raw: str) -> tuple[str, str]:
        """Split a bind-family ``provider:value`` spelling for one node.

        The provider set is closed per node, so splitting on the first colon
        is unambiguous: a path such as ``/x:y`` yields the non-provider ``/x``
        and fails with the node's accepted spellings.
        """

        node = self.answerable(name, CARRIER_FAMILY_BIND)
        provider, separator, value = raw.partition(":")
        if not separator or provider not in node.providers or not value:
            expected = " or ".join(f"{provider}:VALUE" for provider in node.providers)
            raise ProjectConfigurationError(
                f"Binding {name!r} must be spelled {expected}; got {raw!r}."
            )
        return provider, value


def build_node_registry(
    manifest: Mapping[str, Any], lock: Mapping[str, Any]
) -> NodeRegistry:
    """Derive the registry from one project's manifest and platform lock."""

    nodes: list[ConfigurationNode] = []
    for name, value_declaration in configuration_value_declarations(manifest).items():
        nodes.append(
            ConfigurationNode(
                name=name,
                family=CARRIER_FAMILY_SET,
                description=str(value_declaration.get("description") or ""),
                required=bool(value_declaration.get("required", False)),
                declaration=value_declaration,
            )
        )
    for name, binding in configuration_binding_declarations(lock).items():
        nodes.append(
            ConfigurationNode(
                name=name,
                family=CARRIER_FAMILY_BIND,
                description=binding.description,
                # Directory slots always have the managed-state default, so
                # they can never block resolution.
                required=False,
                declaration=binding,
                providers=(PROVIDER_HOST_DIRECTORY,),
            )
        )
    for name, secret in component_secret_inputs(lock).items():
        nodes.append(
            ConfigurationNode(
                name=name,
                family=CARRIER_FAMILY_BIND,
                description=secret.description,
                required=secret.required,
                declaration=secret,
                providers=(PROVIDER_HOST_ENVIRONMENT,),
            )
        )
    for name, authorization in authorization_declarations(manifest, lock).items():
        nodes.append(
            ConfigurationNode(
                name=name,
                family=CARRIER_FAMILY_AUTHORIZE,
                description=authorization.description,
                # Only the base image blocks resolution when unanswered; every
                # other authorization is a recommendation the consumer may
                # decline.
                required=name == "base-image",
                declaration=authorization,
                accepts_justification=name in CURATED_HOST_RECOMMENDATIONS,
            )
        )
    return NodeRegistry(nodes)
