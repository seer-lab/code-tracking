package org.jetbrains.research.tasktracker.plugins.requests

import io.ktor.http.*
import io.ktor.server.application.*
import io.ktor.server.plugins.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import io.ktor.server.util.*
import org.jetbrains.exposed.sql.and
import org.jetbrains.exposed.sql.transactions.transaction
import org.jetbrains.research.tasktracker.database.models.User
import org.jetbrains.research.tasktracker.database.models.Users

fun Routing.createUser() {
    post("/create-user") {
        val formParameters = call.receiveParameters()
        try {
            val userId = transaction {
                val pin = formParameters.getOrFail("pin")
                getUserId(pin)
            }
            call.respondText(
                userId.toString(),
                status = HttpStatusCode.OK
            )
        } catch (e: IllegalArgumentException) {
            call.respond(HttpStatusCode.BadRequest, e.localizedMessage)
        } catch (e: MissingRequestParameterException) {
            call.respond(HttpStatusCode.BadRequest, e.localizedMessage)
        }
    }
}

@Suppress("SwallowedException")
fun getUserId(pin: String): Int {
    val user = User.find { (Users.pin eq pin) }
    if (user.empty()) {
        return User.new {
            this.pin = pin
        }.id.value
    }
    return user.first().id.value
}
