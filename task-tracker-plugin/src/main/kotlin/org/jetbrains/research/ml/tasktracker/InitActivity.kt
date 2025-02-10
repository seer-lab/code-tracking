package org.jetbrains.research.ml.tasktracker

import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.project.Project
import com.intellij.openapi.startup.ProjectActivity
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import org.jetbrains.research.ml.tasktracker.tracking.TaskFileHandler

class InitActivity : ProjectActivity {
    private val logger: Logger = Logger.getInstance(javaClass)

    init {
        logger.info("${Plugin.PLUGIN_NAME}: ProjectActivity initialized")
    }

    override suspend fun execute(project: Project) {
        logger.info("${Plugin.PLUGIN_NAME}: Executing ProjectActivity")
        GlobalScope.launch {
            try {
                Plugin.installRequiredPlugins(project) // Install plugins (background task)
                delay(5000) // Delay to ensure proper initialization
                TaskFileHandler.addProject(project) // Add project after initialization
                logger.info("${Plugin.PLUGIN_NAME}: Initialization complete")
            } catch (e: Exception) {
                logger.error("${Plugin.PLUGIN_NAME}: Failed during initialization", e)
            }
        }
    }
}
