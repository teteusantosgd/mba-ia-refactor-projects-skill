// Driver sqlite3 sem `.verbose()` (overhead/diagnóstico desnecessário fora de debug).
const sqlite3 = require('sqlite3');

// Cria a conexão e expõe um cliente com API baseada em Promise (async/await),
// eliminando o callback hell. `run` preserva lastID/changes do driver.
function createDbClient() {
    const db = new sqlite3.Database(':memory:');

    return {
        get(sql, params = []) {
            return new Promise((resolve, reject) => {
                db.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
            });
        },
        all(sql, params = []) {
            return new Promise((resolve, reject) => {
                db.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
            });
        },
        run(sql, params = []) {
            return new Promise((resolve, reject) => {
                db.run(sql, params, function (err) {
                    if (err) return reject(err);
                    resolve({ lastID: this.lastID, changes: this.changes });
                });
            });
        },
        exec(sql) {
            return new Promise((resolve, reject) => {
                db.exec(sql, (err) => (err ? reject(err) : resolve()));
            });
        },
    };
}

// Cria o schema e popula os seeds. A senha do seed é armazenada com hash forte,
// nunca em texto puro.
async function initializeDatabase(dbClient, { passwordService }) {
    await dbClient.exec(`
        CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT);
        CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER);
        CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER);
        CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT);
        CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME);
    `);

    const seedPasswordHash = passwordService.hash('123');
    await dbClient.run(
        'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
        ['Leonan', 'leonan@fullcycle.com.br', seedPasswordHash],
    );
    await dbClient.run(
        'INSERT INTO courses (title, price, active) VALUES (?, ?, ?), (?, ?, ?)',
        ['Clean Architecture', 997.0, 1, 'Docker', 497.0, 1],
    );
    await dbClient.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [1, 1]);
    await dbClient.run(
        'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
        [1, 997.0, 'PAID'],
    );
}

module.exports = { createDbClient, initializeDatabase };
