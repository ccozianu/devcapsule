# Round 1 of generalization review #255

Your session-log fix and test are accepted in principle. Keep them. Two
reported limitations contradict this slice's contracts and must be addressed
before acceptance. They do not require a comprehensive Docker option schema.

1. Do not corrupt unrelated argument operands through set-env/unset-env.
   The implementor reproduced a valid Docker invocation with these tokens:

       ["--label", "-eTOKEN=label-only", "--env", "TOKEN=before"]

   Docker accepted it and the container saw TOKEN=before. update_environment
   currently turns it into ["--label", "--env", "TOKEN=after"], removing the
   label's value. The work order requires convenience edits to preserve
   unrelated arguments. Fix the bounded environment helper, with regressions
   for flag-looking operands and real adjacent env options. Either preserve
   those operands correctly, or refuse ambiguous convenience operations
   before any write, with a clear value-free remedy to replace the full list
   using set-extra-docker-args. Conservative refusal is permitted when there
   is insufficient information; silent corruption is not. Apply consistent
   handling to list-env so it does not invent environment variables from
   other option values. Keep set-extra-docker-args and actual launch tokens
   literal; diagnostic redaction may remain conservative. No full Docker
   schema or general parsing redesign is requested. Document any refusal.

2. Reject the attached value forms of already-known launcher-owned short
   options, at least -m2g and -u1000, before saving and when launching saved
   options. The existing map already identifies -m and -u; recognize their
   attached spelling without inspecting arbitrary option payloads. Preserve
   -eNAME=value and -vSOURCE:DEST. The current rejection deliberately may
   refuse an option-looking operand too; its existing contract says this.
   Add focused regressions. This is closing the existing boundary reused by
   the changed feature, not a new Docker schema.

Read the assessment on #255. Work on the same review branch and checkout.
Keep the previous scope and restrictions: no status/evidence/work-order edits,
no merges or rebases, no containers, no real credentials. Run focused tests
and the full gate as in the initial brief, with a /tmp basetemp and a log
outside it. Commit, push, update the PR body with the fixes and validation,
then reply on #255. Last line: the comment URL. Stop on an access blocker.
