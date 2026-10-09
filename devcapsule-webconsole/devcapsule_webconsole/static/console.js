// The console's one script. Each page names itself with data-page on <body>;
// the matching renderer fetches the page's document from /api and builds the
// DOM with textContent only, never markup from data.
(function () {
  "use strict";

  async function api(path) {
    const response = await fetch(path, { credentials: "same-origin" });
    let body = null;
    try { body = await response.json(); } catch (error) { body = null; }
    if (!response.ok) {
      const detail = body && body.error ? body.error + (body.stderr ? "\n" + body.stderr : "") : "HTTP " + response.status;
      throw new Error(path + ": " + detail);
    }
    return body;
  }

  function el(tag, attributes, children) {
    const node = document.createElement(tag);
    for (const [name, value] of Object.entries(attributes || {})) {
      if (name === "text") node.textContent = value;
      else node.setAttribute(name, value);
    }
    for (const child of children || []) node.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
    return node;
  }

  function scalar(value) {
    if (value === null || value === undefined) return "—";
    if (typeof value === "object") return JSON.stringify(value);
    return String(value);
  }

  function facts(pairs) {
    const list = el("dl", { class: "facts" });
    for (const [label, value] of pairs) {
      list.appendChild(el("dt", { text: label }));
      list.appendChild(el("dd", { text: scalar(value) }));
    }
    return list;
  }

  function table(columns, rows) {
    const head = el("tr", {}, columns.map((column) => el("th", { text: column.label })));
    const body = rows.map((row) => el("tr", {}, columns.map((column) =>
      el("td", { text: scalar(typeof column.key === "function" ? column.key(row) : row[column.key]) }))));
    return el("table", { class: "data" }, [el("thead", {}, [head]), el("tbody", {}, body)]);
  }

  function tree(value) {
    if (value === null || typeof value !== "object") return el("span", { class: "scalar", text: scalar(value) });
    const entries = Array.isArray(value) ? value.map((item, index) => [String(index), item]) : Object.entries(value);
    return el("ul", { class: "tree" }, entries.map(([key, item]) => {
      const child = el("li", {}, [el("span", { class: "key", text: key + ": " })]);
      child.appendChild(tree(item));
      return child;
    }));
  }

  function components(object) {
    return table([{ key: "name", label: "Component" }, { key: "version", label: "Version" }],
      Object.entries(object || {}).map(([name, version]) => ({ name, version })));
  }

  function fail(container, error) {
    container.replaceChildren(el("div", { class: "failure", text: String(error.message || error) }));
  }

  function section(container, title, node) {
    container.appendChild(el("h2", { text: title }));
    container.appendChild(node);
  }

  const pages = {
    async home(container) {
      const identity = await api("/api/identity");
      const project = identity.project || {};
      const checkout = identity.checkout || {};
      const base = identity.base || {};
      const set = identity["version-set"] || {};
      container.replaceChildren(facts([
        ["Context", identity.context],
        ["Project", [project.creator, project.slug].filter(Boolean).join("/") + (project.name ? " — " + project.name : "")],
        ["Checkout", checkout.name ? checkout.name + " at " + (checkout["launcher-path"] || "") : checkout["launcher-path"]],
        ["Runtime path", checkout["runtime-path"]],
        ["Version set", set.identity ? set.identity + " (" + set.origin + ")" : null],
        ["Base", base.reference ? base.reference + (base["build-mnemonic"] ? " — " + base["build-mnemonic"] : "") : null],
        ["Console", identity["console-version"]],
      ]));
    },

    async configuration(container) {
      const listing = await api("/api/configuration");
      const checkout = listing.checkout || {};
      container.replaceChildren();
      if (listing.rows) {
        container.appendChild(facts([
          ["Context", listing.context],
          ["Checkout", checkout.name],
          ["Launcher path", checkout["launcher-path"]],
          ["Checkout input", checkout.input],
          ["Generated plan", checkout.resolution],
        ]));
        section(container, "Recorded values, bindings, secrets, authorizations and the resolution", table([
          { key: "kind", label: "Kind" }, { key: "name", label: "Name" }, { key: "status", label: "Status" },
          { key: "source", label: "Source" }, { key: "value", label: "Value / recommendation" },
        ], listing.rows));
        return;
      }
      container.appendChild(el("p", { class: "notice",
        text: "Read-only launcher configuration for the next launch. Host paths and permissions are recorded choices, not observations of this session." }));
      container.appendChild(facts([
        ["Context", listing.context],
        ["Checkout", checkout.name],
        ["Launcher path", checkout["launcher-path"]],
        ["Runtime path", checkout["runtime-path"]],
      ]));
      section(container, "The mounted checkout record", tree(checkout.record));
      section(container, "To change configuration, outside this capsule", el("p", {}, [el("code", { text: listing["launcher-command"] })]));
    },

    async versions(container) {
      const document_ = await api("/api/versions");
      container.replaceChildren();
      const describe = (set) => {
        const block = el("div");
        block.appendChild(facts([["Version set", set.identity], ["Origin", set.origin], ["Platform", set.platform], ["Base", set.base],
          ["Local base override", set["local-base-override"]]].filter(([, value]) => value !== undefined)));
        block.appendChild(components(set.components));
        return block;
      };
      if (document_.context === "running capsule") {
        section(container, "Running session", describe(document_.running));
        if (document_["next-launch"]) {
          section(container, "Selected for next launch", describe(document_["next-launch"]));
          container.appendChild(el("p", { class: "notice", text: document_["selection-changed"]
            ? "Selection has changed; this running session remains on its launch-time version set."
            : "Same software selection as this session." }));
        } else {
          section(container, "Selected for next launch", el("p", { class: "failure", text: "Unavailable: " + document_["next-launch-unavailable"] }));
        }
        section(container, "To inspect or change the selection, outside this capsule", el("p", {}, [el("code", { text: document_["launcher-command"] })]));
        return;
      }
      section(container, "Selected for the next launch", describe(document_.selected));
      const recommendation = document_["project-recommendation"];
      if (recommendation) {
        container.appendChild(el("p", { class: "notice", text: "Project recommendation: " + recommendation.status + (recommendation.detail ? " — " + recommendation.detail : "") }));
      }
      const validation = document_.validation || {};
      section(container, "Validation", el("ul", {}, [
        ...(validation.evidence || []).map((item) => el("li", { text: "DevCapsule validation: " + item })),
        ...(validation["not-yet-validated"] || []).map((item) => el("li", { text: "Not yet validated: " + item })),
      ]));
      const use = document_["local-use"] || {};
      container.appendChild(el("p", { text: use["zero-exit-launch-recorded"]
        ? "Local use: a zero-exit launch is recorded (not comprehensive validation)." : "Local use: no successful launch recorded." }));
    },

    async project(container) {
      const info = await api("/api/project");
      const project = info.project || {};
      const checkout = info.checkout || {};
      container.replaceChildren(facts([
        ["Context", info.context],
        ["Project", [project.creator, project.slug].filter(Boolean).join("/") + (project.name ? " — " + project.name : "")],
        ["Checkout", checkout.name],
        ["Launcher path", checkout["launcher-path"]],
        ["Runtime path", checkout["runtime-path"]],
        ["Base", info.base ? [info.base.reference, info.base["build-mnemonic"]].filter(Boolean).join(" — ") : null],
        ["Running selection", info["running-selection"]],
      ].filter(([, value]) => value !== undefined)));
      section(container, "Components", components(info.components));
      if (info["next-launch-components"]) section(container, "Components selected for the next launch", components(info["next-launch-components"]));
      section(container, "Environment", table([
        { key: "name", label: "Variable" }, { key: "value", label: "Value" }, { key: "purpose", label: "Purpose" }, { key: "source", label: "Source" },
      ], info.environment || []));
      section(container, "Persistence", table([
        { key: "name", label: "Name" }, { key: "path", label: "Path in the capsule" }, { key: "backing", label: "Backing on the host" },
        { key: "kind", label: "Kind" }, { key: "scope", label: "Scope" }, { key: "lifecycle", label: "Lifecycle" },
      ], info.persistence || []));
      section(container, "Temporary", el("ul", {}, (info.temporary || []).map((item) => el("li", { text: scalar(item) }))));
      section(container, "Notes", el("ul", {}, (info.notes || []).map((item) => el("li", { text: item }))));
    },
  };

  function bytes(value) {
    if (value === null || value === undefined) return "—";
    const units = ["B", "KiB", "MiB", "GiB", "TiB"];
    let number = value, unit = 0;
    while (number >= 1024 && unit < units.length - 1) { number /= 1024; unit += 1; }
    return (unit === 0 ? number : number.toFixed(1)) + " " + units[unit];
  }

  function meter(label, value, percent, detail) {
    const fill = el("span");
    if (percent !== null && percent !== undefined) {
      fill.style.width = Math.max(0, Math.min(100, percent)) + "%";
      if (percent >= 90) fill.classList.add("hot");
    }
    return el("div", { class: "meter" }, [
      el("div", { class: "label", text: label }),
      el("div", { class: "value", text: value }),
      el("div", { class: "bar" }, [fill]),
      el("div", { class: "detail", text: detail }),
    ]);
  }

  pages.processes = async function (container) {
    const REFRESH_MS = 3000;
    let paused = false;
    let timer = null;
    let refreshing = false;
    let lastStatus = "Loading…";
    const meters = el("div", { class: "meters" });
    const status = el("span", { text: "Loading…" });
    const button = el("button", { type: "button", text: "Pause" });
    const table = el("div");
    button.addEventListener("click", () => {
      paused = !paused;
      button.textContent = paused ? "Resume" : "Pause";
      if (timer !== null) { clearTimeout(timer); timer = null; }
      status.textContent = lastStatus + (paused ? " · paused" : "");
      if (!paused) refresh();
    });
    container.replaceChildren(meters, el("div", { class: "toolbar" }, [button, status]), table);

    async function refresh() {
      if (paused || refreshing) return;
      refreshing = true;
      if (timer !== null) { clearTimeout(timer); timer = null; }
      try {
        const [resources, listing] = await Promise.all([api("/api/resources"), api("/api/processes")]);
        if (paused) return;
        const cpu = resources.cpu || {}, memory = resources.memory || {}, pids = resources.pids || {};
        meters.replaceChildren(
          meter("CPU", cpu.percent === null || cpu.percent === undefined ? "—" : cpu.percent + " %", cpu.percent,
            resources.available
              ? "of " + cpu["available-cpus"] + (cpu["limit-cpus"] ? " CPUs (cgroup quota)" : " CPUs (no readable quota)") +
                "; " + (cpu["usage-seconds"] === null ? "" : cpu["usage-seconds"] + " s used since start")
              : "the capsule's cgroup is not readable here"),
          meter("Memory", bytes(memory["current-bytes"]), memory.percent,
            (memory["limit-bytes"] != null ? "of " + bytes(memory["limit-bytes"]) + " limit" : "limit unavailable or unlimited") +
            (memory["anon-bytes"] !== null && memory["anon-bytes"] !== undefined
              ? "; anonymous " + bytes(memory["anon-bytes"]) + ", file " + bytes(memory["file-bytes"]) : "")),
          meter("Tasks (threads)", scalar(pids.current), pids.current != null && pids.max > 0 ? (pids.current / pids.max) * 100 : null,
            (pids.max != null ? "of " + pids.max + " task limit" : "limit unavailable or unlimited") +
            "; " + listing.count + " processes listed"),
        );
        table.replaceChildren(table_(listing.processes));
        lastStatus = "Sampled " + resources["sampled-at"] + " over " + resources["interval-seconds"] + " s";
        status.textContent = lastStatus;
      } catch (error) {
        if (!paused) {
          meters.replaceChildren();
          lastStatus = "Refresh failed";
          status.textContent = lastStatus;
          fail(table, error);
        }
      } finally {
        refreshing = false;
        if (!paused) timer = setTimeout(refresh, REFRESH_MS);
      }
    }

    function table_(rows) {
      // Only the command wraps; every other column keeps its word whole.
      const columns = [
        { key: "pid", label: "PID", class: "num" }, { key: "user", label: "User", class: "keep" },
        { key: "name", label: "Name", class: "keep" }, { key: "cpu-percent", label: "CPU %", class: "num" },
        { key: (row) => bytes(row["rss-bytes"]), label: "RSS", class: "num" },
        { key: "status", label: "Status", class: "keep" }, { key: "command", label: "Command", class: "" },
      ];
      const head = el("tr", {}, columns.map((column) => el("th", { class: column.class, text: column.label })));
      const body = rows.map((row) => el("tr", {}, columns.map((column) =>
        el("td", { class: column.class, text: scalar(typeof column.key === "function" ? column.key(row) : row[column.key]) }))));
      return el("table", { class: "data" }, [el("thead", {}, [head]), el("tbody", {}, body)]);
    }

    await refresh();
  };

  document.addEventListener("DOMContentLoaded", () => {
    const page = document.body.dataset.page;
    const container = document.getElementById("content");
    for (const link of document.querySelectorAll("header nav a")) {
      if (link.getAttribute("href") === window.location.pathname) link.setAttribute("aria-current", "page");
    }
    if (page && pages[page] && container) {
      pages[page](container).catch((error) => fail(container, error));
    }
  });
})();
