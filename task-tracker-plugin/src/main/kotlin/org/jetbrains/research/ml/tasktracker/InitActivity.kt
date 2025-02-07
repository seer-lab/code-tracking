package org.jetbrains.research.ml.tasktracker

import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.project.Project
import com.intellij.openapi.startup.StartupActivity
import org.jetbrains.research.ml.tasktracker.tracking.TaskFileHandler

class InitActivity : StartupActivity {
    private val logger: Logger = Logger.getInstance(javaClass)

    init {
        logger.info("${Plugin.PLUGIN_NAME}: Startup activity initialized")
    }

    override fun runActivity(project: Project) {
        logger.info("${Plugin.PLUGIN_NAME}: Running startup activity")
        try {
            Plugin.installRequiredPlugins(project)
            TaskFileHandler.addProject(project)
            logger.info("${Plugin.PLUGIN_NAME}: Initialization complete")
        } catch (e: Exception) {
            logger.error("${Plugin.PLUGIN_NAME}: Failed during initialization", e)
        }
    }
}
