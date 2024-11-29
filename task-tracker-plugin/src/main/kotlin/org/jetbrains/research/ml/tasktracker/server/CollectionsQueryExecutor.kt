package org.jetbrains.research.ml.tasktracker.server

import kotlinx.serialization.KSerializer
import kotlinx.serialization.builtins.ListSerializer
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonConfiguration
import okhttp3.Request
import okhttp3.Response
import java.net.URL

object CollectionsQueryExecutor : QueryExecutor() {

    fun <T> getCollection(url: String, serializer: KSerializer<T>): List<T> {
        return parseResponse(getResponse(url), serializer) { ListSerializer(it) }
    }

    fun <T> getItemFromCollection(url: String, serializer: KSerializer<T>): T {
        return parseResponse(getResponse(url), serializer) { it }
    }


    private fun <T, R> parseResponse(
        response: Response?,
        serializer: KSerializer<T>,
        transform: (KSerializer<T>) -> KSerializer<R>
    ): R {
        if (response?.isSuccessful() == true) {
            // Use the custom Json instance with allowStructuredMapKeys = true
            return customJson.decodeFromString(transform(serializer), response.body?.string() ?: "")
        }
        throw IllegalStateException("Unsuccessful server response")
    }

    private fun getResponse(url: String): Response? {
        return executeQuery(Request.Builder().url(URL("${baseUrl}${url}")).build())
    }

    private val customJson = Json {
        allowStructuredMapKeys = true
    }

}