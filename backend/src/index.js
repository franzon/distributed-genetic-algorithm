/*
Descrição: Backend prinicpal
Autor: Jorge Rossi
Data: 23/11/2019
*/

const express = require('express')
const cors = require('cors')
const redis = require('redis')
const knexConfig = require('../knexfile').development
const knex = require('knex')(knexConfig);

const app = express()
app.use(cors())
app.use(express.json())

const subscriber = redis.createClient({ host: 'redis', port: 6379 })

// Quando redis recebe uma mensagem -> algum cliente enviando uma solução
subscriber.on("message", async (channel, message) => {
    try {
        const data = JSON.parse(message)
        const taskId = Number.parseInt(channel.split("_")[1])
        if (data.status === "completed") {
            knex('tasks').where({ task_id: taskId }).update({ status: 'completed' })
            subscriber.unsubscribe(channel)

        } else {

            const solutions = await knex('solutions').select('id', 'user_name', 'genome', 'fitness').where({ task_id: taskId }).orderBy('fitness', 'desc').limit(20)
            const worstBestSolution = solutions.pop()

            if (!worstBestSolution || data.fitness > worstBestSolution.fitness) {
                console.log("inserindo nova no ranking", data.fitness)
                await knex('solutions').insert({ user_name: data.user_name, genome: data.genome, fitness: data.fitness, task_id: taskId })
            }
        }
    } catch (error) {
        console.log(error)
    }
})

// Rota para criação de tasks
app.post('/task', async (req, res) => {
    try {
        const id = await knex('tasks').insert({ user_name: req.body.user_name, algorithm_id: req.body.algorithm_id })

        console.log('se inscrevendo em ' + "task_" + id.toString())
        subscriber.subscribe("task_" + id.toString())
        res.json({ status: "created" })
    } catch (error) {
        res.json({ status: error })
    }
})

// Rota para listar tasks
app.get('/task', async (req, res) => {
    try {
        const status = req.query.filter || "pending"
        const data = await knex('tasks').select('id', 'user_name', 'algorithm_id', 'status')
        res.json(data)
    } catch (error) {
        res.json({ status: error })
    }
})

// Rota para listar melhores soluções de uma task
app.get('/task/:id/best', async (req, res) => {
    try {
        const data = await knex('solutions').select('id', 'user_name', 'genome', 'fitness').where({ task_id: req.params.id }).orderBy('fitness', 'desc').limit(20)
        res.json(data)
    } catch (error) {
        res.json({ status: error.toString() })
    }
})

app.listen(3333, async () => {
    console.log('Servidor executando na porta 3333')

    // Se inscreve em todas as tasks não concluídas
    const data = await knex('tasks').select('id').where({ status: 'pending' })
    for (const task of data) {
        subscriber.subscribe("task_" + task.id.toString())
    }

})