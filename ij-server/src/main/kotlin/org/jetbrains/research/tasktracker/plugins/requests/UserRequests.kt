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
            val pin = formParameters.getOrFail("pin")
            val name = "test_Bisha_name"
            val userId = transaction {
                getUserId(pin)
            }
            
            if (userId != null) {
                call.respondText(
                    userId.toString(),
                    status = HttpStatusCode.OK
                )
            } else {
                call.respond(HttpStatusCode.InternalServerError, "Failed to create or retrieve user")
            }
        } catch (e: IllegalArgumentException) {
            call.respond(HttpStatusCode.BadRequest, e.localizedMessage ?: "Bad request")
        } catch (e: MissingRequestParameterException) {
            call.respond(HttpStatusCode.BadRequest, e.localizedMessage ?: "Missing parameter")
        } catch (e: Exception) {
            call.respond(HttpStatusCode.InternalServerError, "Server error: ${e.localizedMessage ?: e.message}")
        }
    }
}

@Suppress("SwallowedException")
fun getUserId(pin: String): Int? {
    return try {
        val user = User.find { (Users.pin eq pin) }
        if (user.empty()) {
            User.new {
                this.pin = pin
            }.id.value
        } else {
            user.first().id.value
        }
    } catch (e: Exception) {
        null
    }
}
