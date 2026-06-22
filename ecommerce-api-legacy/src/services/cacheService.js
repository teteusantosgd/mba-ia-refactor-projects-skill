// Cache com estado encapsulado e ciclo de vida controlado (injetado via DI),
// substituindo a variável global mutável `globalCache`.
class CacheService {
    constructor() {
        this.store = new Map();
    }

    set(key, value) {
        this.store.set(key, value);
    }

    get(key) {
        return this.store.get(key);
    }
}

module.exports = CacheService;
