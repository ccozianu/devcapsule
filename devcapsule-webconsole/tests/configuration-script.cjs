// Run the actual configuration page against a small DOM and controlled HTTP responses.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
class Node {
  constructor(tag) { this.tag = tag; this.attributes = {}; this.children = []; this.listeners = {}; }
  setAttribute(key, value) { this.attributes[key] = value; if (key === 'value') this.value = value; }
  appendChild(child) { this.children.push(child); return child; }
  replaceChildren(...children) { this.children = children; }
  addEventListener(name, callback) { this.listeners[name] = callback; }
}
const descendants = node => node.children.flatMap(child => [child, ...descendants(child)]);
const flush = () => new Promise(resolve => setImmediate(resolve));
const source = fs.readFileSync(path.join(__dirname, '../devcapsule_webconsole/static/console.js'), 'utf8');
async function page(channel) {
  const content = new Node('main'), handlers = {}, timers = [];
  const state = {refusal: '', error: '', requests: [], writes: [], failRead: false};
  const document = {
    body: {dataset: {page: 'configuration'}},
    createElement: tag => new Node(tag),
    createTextNode: text => Object.assign(new Node('#text'), {textContent: text}),
    getElementById: id => id === 'content' ? content : descendants(content).find(n => n.attributes.id === id),
    querySelector: () => null, querySelectorAll: () => [],
    addEventListener: (name, fn) => { handlers[name] = fn; },
  };
  vm.runInNewContext(source, {
    document, window: {location: {pathname: '/configuration'}},
    setTimeout: fn => timers.push(fn), setInterval() {},
    fetch: async (url, options) => {
      assert.equal(options.credentials, 'same-origin');
      if (options.method === 'POST') {
        state.writes.push(JSON.parse(options.body));
        if (state.error) throw new Error(state.error);
        if (state.refusal) return {ok: false, text: async () => state.refusal};
        state.requests = [{id: 'one', command: 'config deny network', requested: 'now', widening: false, result: null}];
        return {ok: true, json: async () => ({request: state.requests[0]})};
      }
      if (url === '/api/configuration') return {ok: true, json: async () => ({channel, at: 'now', checkout: {},
        'launcher-command': 'devcapsule project config show', rows: [
          {kind: 'console', name: 'prior', pending: 'confirm prior request', command: 'config console apply prior'},
          {kind: 'ide', name: 'ide', pending: 'choose IDE', request: 'ide python-ide'},
          {kind: 'access', name: 'docker-daemon', exposure: 'Broad host control', reason: 'Project build containers'},
        ]})};
      assert.equal(url, '/api/configuration/requests');
      if (state.failRead) return {ok: false, status: 502, json: async () => ({error: 'unreadable'})};
      return {ok: true, json: async () => ({requests: state.requests})};
    },
  });
  handlers.DOMContentLoaded(); await flush();
  return {content, state, timers};
}
(async () => {
  const absent = await page(false);
  assert.equal(descendants(absent.content).filter(n => n.tag === 'form').length, 0);
  assert.ok(descendants(absent.content).some(n => (n.textContent || '').includes('no usable configuration channel')));
  const {content, state, timers} = await page(true);
  const forms = descendants(content).filter(n => n.tag === 'form');
  assert.ok(descendants(content).some(n => n.textContent === 'Broad host control'));
  assert.ok(descendants(content).some(n => n.textContent === 'Project build containers'));
  assert.equal(forms.length, 2); // Earlier deferred requests require the host, not a new console request.
  assert.ok(descendants(content).some(n => (n.textContent || '').includes('Confirm on the host: config console apply prior')));
  const form = forms[0], button = form.children.find(n => n.tag === 'button');
  const status = form.children.find(n => n.attributes.class === 'request-status');
  state.refusal = 'invalid IDE';
  await form.listeners.submit({preventDefault() {}});
  assert.equal(status.textContent, 'refused: invalid IDE'); assert.equal(button.disabled, false);
  assert.deepEqual(state.writes[0], {command: 'ide python-ide'});
  state.refusal = ''; state.error = 'offline';
  await form.listeners.submit({preventDefault() {}});
  assert.equal(status.textContent, 'failed: offline'); assert.equal(button.disabled, false);
  state.error = '';
  await form.listeners.submit({preventDefault() {}});
  assert.equal(status.textContent, 'sent as one');
  for (let i = 0; i < 60; i++) { assert.ok(timers.length); await timers.shift()(); await flush(); }
  assert.equal(timers.length, 0);
  assert.ok(descendants(content).some(n => (n.textContent || '').includes('No change is confirmed')));
  await form.listeners.submit({preventDefault() {}});
  state.failRead = true;
  await timers.shift()(); await flush();
  assert.ok(descendants(content).some(n => (n.textContent || '').includes('Cannot read the launcher outcome')));
  console.log('Configuration page: absent channel, host confirmation, HTTP refusal, network error and bounded polling passed.');
})().catch(error => {console.error(error); process.exitCode = 1;});
