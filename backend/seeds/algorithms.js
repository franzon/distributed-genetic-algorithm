
exports.seed = function (knex) {
  // Deletes ALL existing entries
  return knex('algorithms').del()
    .then(function () {
      // Inserts seed entries
      return knex('algorithms').insert([
        { id: 1, description: 'Traveling Salesman' },
        { id: 2, description: 'Random word' }
      ]);
    });
};
