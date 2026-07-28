import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { URL } from 'node:url'

const config = readFileSync(new URL('../nginx.conf', import.meta.url), 'utf8')

assert.match(config, /location \/api\/\s*\{[\s\S]*proxy_set_header Host backend;/)
assert.match(config, /proxy_set_header X-Forwarded-Host \$host;/)
assert.doesNotMatch(config, /proxy_set_header Host \$host;/)
