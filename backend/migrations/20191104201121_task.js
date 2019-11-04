
exports.up = function (knex) {
    return knex.schema.createTable('tasks', table => {
        table.increments('id')
        table.string('user_name')
        table.string('task_description')
        table.enu('status', ['pending', 'completed']).defaultTo('pending')
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
    return knex.schema.dropTable('solutions').dropTable('tasks')

};
