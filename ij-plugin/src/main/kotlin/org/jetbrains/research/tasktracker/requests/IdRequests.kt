package org.jetbrains.research.tasktracker.requests

import com.intellij.openapi.diagnostic.Logger
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.cio.*
import io.ktor.client.request.forms.*
import io.ktor.http.*
import kotlinx.coroutines.runBlocking
import org.jetbrains.research.tasktracker.TaskTrackerPlugin
import org.jetbrains.research.tasktracker.config.MainTaskTrackerConfig.Companion.getRoute
import org.jetbrains.research.tasktracker.ui.main.panel.storage.GlobalPluginStorage

object IdRequests {
    private val client = HttpClient(CIO)
    private val logger = Logger.getInstance(IdRequests::class.java)

    @Suppress("TooGenericExceptionCaught")
    fun getUserId(pin: String): Int? =
        runBlocking {
            val url = getRoute("create-user")
            try {
                val response = client.submitForm(
                    url = url,
                    formParameters = mapOf(
                        "pin" to pin,
                        "name" to pin,
                        "email" to "bisha_test@gmail.com",
                    ).buildParameters()
                )
                val statusCode = response.status
                val body = response.body<String>()
                
                if (statusCode.isSuccess()) {
                    return@runBlocking if (body.isNotBlank()) {
                        try {
                            body.toInt()
                        } catch (e: NumberFormatException) {
                            logger.warn("Failed to parse user ID from response body. Status: $statusCode, Body: '$body', Pin: $pin")
                            null
                        }
                    } else {
                        logger.warn("Empty response body from server. Status: $statusCode, URL: $url, Pin: $pin")
                        null
                    }
                } else {
                    logger.warn("Server returned error status. Status: $statusCode, Body: '$body', URL: $url, Pin: $pin")
                    null
                }
            } catch (e: Exception) {
                logger.warn("Server interaction error while getting user id! Url: $url, Pin: $pin", e)
                null
            }
        }

    @Suppress("TooGenericExceptionCaught")
    fun getResearchId(): Int? =
        runBlocking {
            val url = getRoute("create-research")
            val pluginInfoConfig = TaskTrackerPlugin.mainConfig.pluginInfoConfig
                ?: error("MainPageConfig must not be null")
            try {
                requireNotNull(GlobalPluginStorage.userId) { "User id is not defined" }
                val researchId = TaskTrackerPlugin.mainConfig.pluginInfoConfig?.let {
                    it.researchId
                } ?: error("Plugin info config is uninitialized")
                return@runBlocking client.submitForm(
                    url = url,
                    formParameters = mapOf(
                        "name" to pluginInfoConfig.pluginName,
                        "description" to pluginInfoConfig.pluginDescription,
                        "user_id" to GlobalPluginStorage.userId.toString(),
                        "research_unique_id" to researchId
                    ).buildParameters()
                ).body<Int>()
            } catch (e: IllegalArgumentException) {
                logger.warn(e.localizedMessage)
            } catch (e: Exception) {
                logger.warn("Server interaction error while getting research id! Url: $url", e)
            }
            return@runBlocking null
        }

    private fun Map<String, String>.buildParameters() = parameters {
        this@buildParameters.forEach { (name, param) ->
            append(name, param)
        }
    }
}
