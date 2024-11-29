package org.jetbrains.research.ml.tasktracker.ui

import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.project.Project
import com.intellij.ui.components.JBScrollPane
import javafx.application.Platform
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import org.jetbrains.research.ml.tasktracker.Plugin
import org.jetbrains.research.ml.tasktracker.server.*
import org.jetbrains.research.ml.tasktracker.ui.panes.*
import org.jetbrains.research.ml.tasktracker.ui.panes.util.PaneController
import org.jetbrains.research.ml.tasktracker.ui.panes.util.PaneControllerManager
import org.jetbrains.research.ml.tasktracker.ui.panes.util.Updatable
import org.jetbrains.research.ml.tasktracker.ui.panes.util.subscribe
import java.awt.Toolkit
import javax.swing.JComponent
import javax.swing.JPanel

typealias Pane = PaneControllerManager<out PaneController>

internal object MainController {
    private const val SCREEN_HEIGHT = 1080.0
    private val logger: Logger = Logger.getInstance(javaClass)
    private val contents: MutableList<Content> = arrayListOf()

    private val panes: List<Pane> = arrayListOf(
        ErrorControllerManager,
        LoadingControllerManager,
        SurveyControllerManager,
        TaskChoosingControllerManager,
        TaskSolvingControllerManager,
        FinalControllerManager,
        SuccessControllerManager
    )

    internal var visiblePane: Pane? = LoadingControllerManager
        set(value) {
            logger.info("${Plugin.PLUGIN_NAME} $value set visible, current thread is ${Thread.currentThread().name}")
            panes.forEach { it.setVisible(it == value) }
            field = value
        }

    init {
        subscribe(ServerConnectionNotifier.SERVER_CONNECTION_TOPIC, object : ServerConnectionNotifier {
            override fun accept(connection: ServerConnectionResult) {
                logger.info("${Plugin.PLUGIN_NAME} MainController, server connection topic $connection, current thread is ${Thread.currentThread().name}")
                ApplicationManager.getApplication().invokeLater {
                    logger.info("${Plugin.PLUGIN_NAME} MainController, server connection topic $connection in application block, current thread is ${Thread.currentThread().name}")
                    visiblePane = when (connection) {
                        ServerConnectionResult.UNINITIALIZED -> LoadingControllerManager
                        ServerConnectionResult.LOADING -> LoadingControllerManager
                        ServerConnectionResult.FAIL -> {
                            ErrorControllerManager.setRefreshAction { PluginServer.reconnect(it) }
                            ErrorControllerManager
                        }
                        ServerConnectionResult.SUCCESS -> {
                            contents.forEach { it.updatePanesToCreate() }
                            SurveyControllerManager
                        }
                    }
                }
            }
        })

        subscribe(DataSendingNotifier.DATA_SENDING_TOPIC, object : DataSendingNotifier {
            override fun accept(result: DataSendingResult) {
                ApplicationManager.getApplication().invokeLater {
                    visiblePane = when (result) {
                        DataSendingResult.LOADING -> LoadingControllerManager
                        DataSendingResult.FAIL -> {
                            val currentTask = TaskChoosingUiData.chosenTask.currentValue
                            currentTask?.let { task ->
                                ErrorControllerManager.setRefreshAction { PluginServer.sendDataForTask(task, it) }
                            }
                            ErrorControllerManager
                        }
                        DataSendingResult.SUCCESS -> SuccessControllerManager
                    }
                }
            }
        })
    }

    /*   RUN ON EDT (ToolWindowFactory takes care of it) */
    fun createContent(project: Project): JComponent {
        logger.info("${Plugin.PLUGIN_NAME} MainController create content, current thread is ${Thread.currentThread().name}")
        val screenSize = Toolkit.getDefaultToolkit().screenSize
        val scale = screenSize.height / SCREEN_HEIGHT
        val panel = JPanel()
        panel.background = java.awt.Color.WHITE
        ApplicationManager.getApplication().invokeLater {
            contents.add(Content(panel, project, scale, panes))
        }
        PluginServer.checkItInitialized(project)
        return JBScrollPane(panel)
    }

    /**
     * Represents UI content that needs to be created. It contains [panel] to which all [panesToCreateContent] should
     * add their contents.
     */
    data class Content(val panel: JPanel, val project: Project, val scale: Double, var panesToCreateContent: List<Pane>) {
        init {
            logger.info("${Plugin.PLUGIN_NAME} Content init, current thread is ${Thread.currentThread().name}")
            updatePanesToCreate()
        }

        /**
         * RUN ON EDT
         * Looks at all [panesToCreateContent] and checks if any can create content. If so, creates pane contents,
         * adds them to the [panel], and removes created panes from [panesToCreateContent]
         */
        fun updatePanesToCreate() {
            logger.info("${Plugin.PLUGIN_NAME} updatePanesToCreate, current thread is ${Thread.currentThread().name}")
            val (canCreateContentPanes, cantCreateContentPanes) = panesToCreateContent.partition { it.canCreateContent }

            if (canCreateContentPanes.isNotEmpty()) {
                GlobalScope.launch {
                    canCreateContentPanes.map { it.createContent(project, scale) }.forEach { panel.add(it) }

                    // Ensure the UI update happens on the JavaFX thread
                    Platform.runLater {
                        logger.info("${Plugin.PLUGIN_NAME} updatePanesToCreate in platform block, current thread is ${Thread.currentThread().name}")
                        canCreateContentPanes.map { it.getLastAddedPaneController() }.forEach {
                            if (it is Updatable) {
                                it.update()
                            }
                        }
                    }

                    // Update the remaining panes
                    panesToCreateContent = cantCreateContentPanes
                }
            }
        }
    }
}
