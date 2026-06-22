const crypto = require('crypto');

// Hashing forte com scrypt (nativo do Node, sem dependências externas).
// Formato armazenado: "<salt-hex>:<derivedKey-hex>". Substitui a "cripto" caseira.
const SALT_BYTES = 16;
const KEY_LENGTH = 64;

function hash(rawPassword) {
    const salt = crypto.randomBytes(SALT_BYTES).toString('hex');
    const derivedKey = crypto.scryptSync(rawPassword, salt, KEY_LENGTH).toString('hex');
    return `${salt}:${derivedKey}`;
}

function verify(rawPassword, stored) {
    const [salt, key] = String(stored).split(':');
    if (!salt || !key) return false;

    const derivedKey = crypto.scryptSync(rawPassword, salt, KEY_LENGTH).toString('hex');
    return crypto.timingSafeEqual(Buffer.from(key, 'hex'), Buffer.from(derivedKey, 'hex'));
}

module.exports = { hash, verify };
