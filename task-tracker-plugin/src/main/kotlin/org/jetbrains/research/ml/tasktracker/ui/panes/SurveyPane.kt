package org.jetbrains.research.ml.tasktracker.ui.panes

import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.project.Project
import com.intellij.util.messages.Topic
import javafx.beans.binding.Bindings
import javafx.embed.swing.JFXPanel
import javafx.fxml.FXML
import javafx.scene.control.*
import javafx.scene.layout.HBox
import javafx.scene.layout.Pane
import javafx.scene.shape.Polygon
import javafx.scene.text.Text
import org.jetbrains.research.ml.tasktracker.Plugin
import org.jetbrains.research.ml.tasktracker.models.Country
import org.jetbrains.research.ml.tasktracker.models.Gender
import org.jetbrains.research.ml.tasktracker.models.Language
import org.jetbrains.research.ml.tasktracker.server.PluginServer
import org.jetbrains.research.ml.tasktracker.tracking.*
import org.jetbrains.research.ml.tasktracker.ui.panes.util.*
import java.net.URL
import java.util.*
import java.util.function.Consumer
import kotlin.Comparator
import kotlin.reflect.KClass


object SurveyControllerManager : ServerDependentPane<SurveyController>() {
    override val paneControllerClass: KClass<SurveyController> = SurveyController::class
    override val fxmlFilename: String = "survey-ui-form.fxml"
}


// Maybe its possible to make bounded properties instead?
interface SurveyPin : Consumer<Int> {
    companion object {
        val PIN_NOTIFIER = Topic.create("pin change", SurveyPin::class.java)
    }
}

interface CountryComparatorNotifier : Consumer<Comparator<Country>> {
    companion object {
        val COUNTRY_COMPARATOR_TOPIC = Topic.create("country list change", CountryComparatorNotifier::class.java)
    }
}

interface ProgrammingLanguageNotifier : Consumer<Int> {
    companion object {
        val PROGRAMMING_LANGUAGE_TOPIC = Topic.create("programming language change", ProgrammingLanguageNotifier::class.java)
    }
}

object SurveyUiData : LanguagePaneUiData() {
    private val countries: List<Country> = PluginServer.countries
    private val genders: List<Gender> = PluginServer.genders
    private val programmingLanguages: List<Language> = PluginServer.programmingLanguages

    val pin = UiField(-1, SurveyPin.PIN_NOTIFIER, StoredInfoHandler.getIntStoredField(UiLoggedDataHeader.PIN, -1))
    val programmingLanguage = ListedUiField(
        programmingLanguages,
        0,
        ProgrammingLanguageNotifier.PROGRAMMING_LANGUAGE_TOPIC,
        initValue = StoredInfoHandler.getIndexByStoredKey(UiLoggedDataHeader.PROGRAMMING_LANGUAGE, programmingLanguages, 0)
    )

    override fun getData() = listOf(
        pin,
        language
    )
}

class SurveyController(project: Project, scale: Double, fxPanel: JFXPanel, id: Int) :
    LanguagePaneController(project, scale, fxPanel, id) {
    // Age
    @FXML
    private lateinit var pinLabel: Label

    @FXML
    private lateinit var pinTextField: TextField

    // StartWorking
    @FXML
    private lateinit var startWorkingButton: Button

    @FXML
    private lateinit var startWorkingText: Text

    @FXML
    private lateinit var mainPane: Pane

    @FXML
    private lateinit var orangePolygon: Polygon

    @FXML
    private lateinit var bluePolygon: Polygon

    override val paneUiData = SurveyUiData
    private val translations = PluginServer.paneText?.surveyPane

    companion object {
        private const val PE_YEARS_NUMBER_TO_SHOW_MONTHS = 1
    }

    override fun initialize(url: URL?, resource: ResourceBundle?) {
        logger.info("${Plugin.PLUGIN_NAME}:${this::class.simpleName} init controller")
        mainPane.styleProperty().bind(Bindings.concat("-fx-font-size: ${scale}px;"))
        scalePolygons(arrayListOf(orangePolygon, bluePolygon))
        initPin()
        initStartWorkingButton()
        makeTranslatable()
        super.initialize(url, resource)
    }

    private fun initPin() {
        pinTextField.textProperty().addListener { _, oldValue, newValue ->
            if (!newValue.matches("\\d{0,7}".toRegex())) {
                pinTextField.text = oldValue
            }
        }
        pinTextField.textProperty().addListener {_, _, new ->
            paneUiData.pin.uiValue = new.toIntOrNull() ?: paneUiData.pin.defaultValue
        }
        subscribe(SurveyPin.PIN_NOTIFIER, object : SurveyPin {
            override fun accept(newAge: Int) {
                pinTextField.text = newAge.toString()
                startWorkingButton.isDisable = paneUiData.anyRequiredDataDefault()
            }
        })
    }

    private fun initStartWorkingButton() {
        startWorkingButton.onMouseClicked {
            ApplicationManager.getApplication().invokeLater {
                TaskFileHandler.initProjects()
                val surveyInfo: Map<String, String> = UiLoggedData.headers.zip(UiLoggedData.getData(Unit)).toMap()
                StoredInfoWrapper.updateStoredInfo(surveyInfo)
            }
            changeVisiblePane(TaskChoosingControllerManager)
        }
    }

    private fun makeTranslatable() {
        subscribe(LanguageNotifier.LANGUAGE_TOPIC, object : LanguageNotifier {
            override fun accept(newLanguageIndex: Int) {
                if (LanguagePaneUiData.language.dataList.isNotEmpty()) {
                    val newLanguage = LanguagePaneUiData.language.dataList[newLanguageIndex]
                    val surveyPaneText = translations?.get(newLanguage)
                    surveyPaneText?.let {
                        pinLabel.text = it.pin
                        startWorkingText.text = it.startSession
                    }
                } else {
                    logger.warn("Language data list is empty. Defaulting to English.")
                }
            }
        })
    }
}