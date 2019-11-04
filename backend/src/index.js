const express = require('express')
const cors = require('cors')
const redis = require('redis')
const knexConfig = require('../knexfile').development

const knex = require('knex')(knexConfig);

const app = express()
app.use(cors())
app.use(express.json())


const subscriber = redis.createClient()

subscriber.on("message", (channel, message) => {
    try {

    } catch (error) {

    }
})

app.post('/task', async (req, res) => {
    try {
        const id = await knex('tasks').insert({ user_name: req.body.user_name, task_description: req.body.task_description })
        subscriber.subscribe("task_" + id.toString())
        res.json({ status: "created" })
    } catch (error) {
        res.json({ status: error })
    }
})

app.get('/task', async (req, res) => {
    try {
        const status = req.query.filter || "pending"
        const data = await knex('tasks').select('id', 'user_name', 'task_description', 'status')
        res.json(data)
    } catch (error) {
        res.json({ status: error })
    }
})

app.get('/task/:id/best', async (req, res) => {
    try {
        const data = await knex('solutions').select('id', 'user_name', 'genome', 'fitness').where({ task_id: req.params.id }).orderBy('fitness', 'desc').limit(20)
        res.json(data)
    } catch (error) {
        res.json({ status: error.toString() })
    }
})



app.listen(3333, () => {
    console.log('Servidor executando na porta 3333')
})