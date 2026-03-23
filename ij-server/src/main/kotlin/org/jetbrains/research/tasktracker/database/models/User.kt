package org.jetbrains.research.tasktracker.database.models

import org.jetbrains.exposed.dao.Entity
import org.jetbrains.exposed.dao.EntityClass
import org.jetbrains.exposed.dao.id.EntityID
import org.jetbrains.exposed.dao.id.IntIdTable
import org.jetbrains.research.tasktracker.database.models.Users.uniqueIndex

class User(id: EntityID<Int>) : Entity<Int>(id) {
    companion object : EntityClass<Int, User>(Users)

    var pin by Users.pin
}

object Users : IntIdTable() {
    val pin = text("pin")

    init {
        uniqueIndex(pin)
    }
}
