'use strict';
const assert = require('node:assert/strict');
const api = require('./app.js');
assert.equal(typeof api.evaluate, 'function');
console.log(JSON.stringify({ok:true}));
