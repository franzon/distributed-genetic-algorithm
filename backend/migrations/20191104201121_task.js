
exports.up = function (knex) {
    return knex.schema.createTable('algorithms', table => {
        table.increments('id')
        table.string('description')
    }).createTable('tasks', table => {
        table.increments('id')
        table.string('user_name')
        table.enu('status', ['pending', 'completed']).defaultTo('pending')
        table.integer('algorithm_id').references('id').inTable('algorithms')
        table.timestamps()
    }).createTable('solutions', table => {
        table.increments('id')
        table.string('user_name')
        table.string('genome')
        table.decimal('fitness')
        table.integer('task_id').references('id').inTable('tasks')
        table.timestamps()
    })
};

exports.down = function (knex) {
    return knex.schema.dropTable('solutions').dropTable('tasks').dropTable('algorithms')
};
