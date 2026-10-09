// Run the actual decisions page with a small DOM adapter and the vendored renderer.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const staticRoot = path.join(__dirname, '../devcapsule_webconsole/static');
class Node {
  constructor(tag) { this.tag = tag; this.attributes = {}; this.children = []; this.listeners = {}; this.value = ''; }
  setAttribute(key, value) { this.attributes[key] = value; if (key === 'value') this.value = value; }
  appendChild(child) { this.children.push(child); return child; }
  replaceChildren(...children) { this.children = children; }
  addEventListener(name, callback) { this.listeners[name] = callback; }
  querySelectorAll(selector) {
    const match = /^input\[name="([^"]+)"\](:checked)?$/.exec(selector);
    assert.ok(match, selector);
    return descendants(this).filter(node => node.tag === 'input' && node.attributes.name === match[1]
      && (!match[2] || node.checked));
  }
  querySelector(selector) { return this.querySelectorAll(selector)[0]; }
}
function descendants(node) { return node.children.flatMap(child => [child, ...descendants(child)]); }
const container = new Node('main');
let ready;
const document = {
  body: { dataset: { page: 'decisions' } },
  createElement: tag => new Node(tag),
  createTextNode: text => Object.assign(new Node('#text'), { textContent: text }),
  getElementById: id => { assert.equal(id, 'content'); return container; },
  querySelectorAll: () => [],
  addEventListener: (name, fn) => { assert.equal(name, 'DOMContentLoaded'); ready = fn; },
};
const decision = {
  id: 'review', title: '<script>Title</script>', context: '[Guide](docs/guide.md)\n\n<script>bad()</script>',
  items: ['constructor', 'normal'].map(key => ({
    key, title: key, summary: '**Choose**', records: ['docs/guide.md', '../escape.md', 'javascript:bad()'],
    options: [{key: 'yes', label: '<b>Yes</b>'}, {key: 'no', label: 'No'}], multiple: false,
  })),
};
const writes = [];
let refuse = false;
const context = {
  document, window: { location: { pathname: '/decisions/review' },
    markdownit: require(path.join(staticRoot, 'vendor/markdown-it-15.0.2.umd.min.js')) },
  CSS: { escape: value => value },
  fetch: async (url, options) => {
    if (!options.method) return { ok: true, json: async () => ({decision, answer: {answers: {}, 'answered-at': 'old'}}) };
    assert.equal(url, '/api/decisions/review/answer');
    assert.equal(options.method, 'POST');
    assert.equal(options.credentials, 'same-origin');
    assert.equal(options.headers['Content-Type'], 'application/json');
    writes.push(JSON.parse(options.body));
    return { ok: !refuse, text: async () => refuse ? 'Refused' : JSON.stringify({answer: {'answered-at': 'now'}}) };
  },
};
vm.runInNewContext(fs.readFileSync(path.join(staticRoot, 'console.js'), 'utf8'), context);
(async () => {
  ready();
  await new Promise(resolve => setImmediate(resolve));
  const nodes = descendants(container);
  assert.ok(nodes.some(node => node.tag === 'h2' && node.textContent === decision.title));
  assert.ok(nodes.some(node => node.innerHTML?.includes('href="/records/docs/guide.md"')));
  assert.ok(nodes.some(node => node.innerHTML?.includes('&lt;script&gt;bad()&lt;/script&gt;')));
  assert.ok(nodes.some(node => node.tag === 'strong' && node.textContent === ' <b>Yes</b>'));
  const links = nodes.filter(node => node.tag === 'a').map(node => node.attributes.href);
  assert.deepEqual(links, ['/records/docs/guide.md', '#', '#', '/records/docs/guide.md', '#', '#']);
  const form = nodes.find(node => node.tag === 'form');
  assert.ok(form, 'an unanswered constructor item must not crash the page');
  const input = nodes.find(node => node.tag === 'input' && node.attributes.name === 'constructor');
  assert.ok(!input.checked);
  input.checked = true;
  nodes.find(node => node.tag === 'textarea').value = ' overall ';
  const button = nodes.find(node => node.tag === 'button');
  await form.listeners.submit({preventDefault() {}});
  assert.deepEqual(writes[0], {answers: {constructor: {chosen: ['yes'], note: ''}}, note: 'overall'});
  assert.equal(button.disabled, false);
  assert.equal(button.textContent, 'Submit again');
  assert.ok(nodes.some(node => node.textContent?.startsWith('Answer written at now')));
  refuse = true;
  await form.listeners.submit({preventDefault() {}});
  assert.equal(button.disabled, false);
  assert.ok(nodes.some(node => node.textContent === 'Not written: Refused'));
  console.log('Decision script: render, escaped content, record links, constructor key, submit and refusal passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
