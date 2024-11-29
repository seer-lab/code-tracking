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
interface ProgramNotifier : Consumer<Int> {
    companion object {
        val PROGRAM_NOTIFIER = Topic.create("program change", ProgramNotifier::class.java)
    }
}

interface YearNotifier : Consumer<Int> {
    companion object {
        val YEAR_TOPIC = Topic.create("YEAR change", YearNotifier::class.java)
    }
}

interface PeYearsNotifier : Consumer<Int> {
    companion object {
        val PE_YEARS_TOPIC = Topic.create("program experience years change", PeYearsNotifier::class.java)
    }
}

interface PeMonthsNotifier : Consumer<Int> {
    companion object {
        val PE_MONTHS_TOPIC = Topic.create("program experience months change", PeMonthsNotifier::class.java)
    }
}

//interface DifficultyNotifier : Consumer<Int> {
//    companion object {
//        val DIFFICULTY_TOPIC = Topic.create("difficulty change", DifficultyNotifier::class.java)
//    }
//}

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

    val program = UiField(-1, ProgramNotifier.PROGRAM_NOTIFIER, StoredInfoHandler.getIntStoredField(UiLoggedDataHeader.PROGRAM, -1))
    val year = ListedUiField(
        // TODO: Change genders to years. This needs to be done in both the server and plugin
        genders,
        -1,
        YearNotifier.YEAR_TOPIC,
        initValue = StoredInfoHandler.getIndexByStoredKey(UiLoggedDataHeader.YEAR, genders, -1)
    )
    val peYears = UiField(
        -1,
        PeYearsNotifier.PE_YEARS_TOPIC,
        StoredInfoHandler.getIntStoredField(UiLoggedDataHeader.PROGRAM_EXPERIENCE_YEARS, -1)

    )
    val peMonths = UiField(
        -1,
        PeMonthsNotifier.PE_MONTHS_TOPIC,
        StoredInfoHandler.getIntStoredField(UiLoggedDataHeader.PROGRAM_EXPERIENCE_MONTHS, -1),
        false
    )
//    val difficulty = ListedUiField(
//        difficulties,
//        -1,
//        DifficultyNotifier.DIFFICULTY_TOPIC,
//        compareBy { c -> c.translation.getOrDefault(language.currentValue, "") },
//        CountryComparatorNotifier.COUNTRY_COMPARATOR_TOPIC,
//        StoredInfoHandler.getIndexByStoredKey(UiLoggedDataHeader.DIFFICULTY, difficulties, -1)
//    )
    val programmingLanguage = ListedUiField(
        programmingLanguages,
        0,
        ProgrammingLanguageNotifier.PROGRAMMING_LANGUAGE_TOPIC,
        initValue = StoredInfoHandler.getIndexByStoredKey(UiLoggedDataHeader.PROGRAMMING_LANGUAGE, programmingLanguages, 0)
    )

    override fun getData() = listOf(
        program,
        year,
        peYears,
        peMonths,
//        difficulty,
//        programmingLanguage,
        language
    )
}

class SurveyController(project: Project, scale: Double, fxPanel: JFXPanel, id: Int) :
    LanguagePaneController(project, scale, fxPanel, id) {
    // Age
    @FXML
    private lateinit var programLabel: Label

    @FXML
    private lateinit var programTextField: TextField

    // Gender
    @FXML
    private lateinit var yearLabel: Label

    @FXML
    private lateinit var yearGroup: ToggleGroup

    @FXML
    private lateinit var year1: RadioButton

    @FXML
    private lateinit var year2: RadioButton

    @FXML
    private lateinit var year3: RadioButton

    @FXML
    private lateinit var year4: RadioButton

    @FXML
    private lateinit var year5: RadioButton

    @FXML
    private lateinit var year6: RadioButton

    @FXML
    private lateinit var yearRadioButtons: List<RadioButton>

    // Program Experience
    @FXML
    private lateinit var experienceLabel: Label

    @FXML
    private lateinit var peYearsLabel: Label

    @FXML
    private lateinit var peYearsTextField: TextField

    @FXML
    private lateinit var peMonthsHBox: HBox

    @FXML
    private lateinit var peMonthsLabel: Label

    @FXML
    private lateinit var peMonthsTextField: TextField

    // Country
//    @FXML
//    private lateinit var difficultyLabel: Label
//
//    @FXML
//    private lateinit var difficultyComboBox: ComboBox<Country>
//    private lateinit var difficultyObservableList: ObservableList<Country>

    // Programming language
//    @FXML
//    private lateinit var programmingLanguageLabel: Label
//
//    @FXML
//    private lateinit var programmingLanguageComboBox: ComboBox<String>

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
        initProgram()
        initYear()
        initPeYears()
        initPeMonths()
//        initDifficulty()
//        initProgrammingLanguage()
        initStartWorkingButton()
        makeTranslatable()
        super.initialize(url, resource)
    }

    private fun initProgram() {
        programTextField.addIntegerFormatter(regexFilter("[1-9][0-9]{0,1}"))
        programTextField.textProperty().addListener { _, _, new ->
            paneUiData.program.uiValue = new.toIntOrNull() ?: paneUiData.program.defaultValue
        }
        subscribe(ProgramNotifier.PROGRAM_NOTIFIER, object : ProgramNotifier {
            override fun accept(newAge: Int) {
                programTextField.text = newAge.toString()
                startWorkingButton.isDisable = paneUiData.anyRequiredDataDefault()
            }
        })
    }

    private fun initYear() {
        //TODO: Change all gender references to year
        yearRadioButtons = listOf(year1, year2, year3, year4, year5, year6)
        val gendersSize = paneUiData.year.dataList.size
        yearRadioButtons.forEachIndexed { i, rb -> rb.isVisible = i < gendersSize }

        yearGroup.selectedToggleProperty().addListener { _, _, new ->
            paneUiData.year.uiValue = yearRadioButtons.indexOf(new)
        }
        subscribe(YearNotifier.YEAR_TOPIC, object : YearNotifier {
            override fun accept(newGenderIndex: Int) {
                if (paneUiData.year.isValid(newGenderIndex)) {
                    yearGroup.selectToggle(yearRadioButtons[newGenderIndex])
                    startWorkingButton.isDisable = paneUiData.anyRequiredDataDefault()
                }
            }
        })
    }

    private fun initPeYears() {
        peYearsTextField.addIntegerFormatter(regexFilter("0|[1-9][0-9]{0,1}"))
        peYearsTextField.textProperty().addListener { _, _, new ->
            paneUiData.peYears.uiValue = new.toIntOrNull() ?: paneUiData.peYears.defaultValue
        }
        subscribe(PeYearsNotifier.PE_YEARS_TOPIC, object : PeYearsNotifier {
            override fun accept(newPeYears: Int) {
                peYearsTextField.text = newPeYears.toString()
                val isPeMonthsRequired =
                    !paneUiData.peYears.isUiValueDefault && newPeYears < PE_YEARS_NUMBER_TO_SHOW_MONTHS
                paneUiData.peMonths.isRequired = isPeMonthsRequired
                peMonthsHBox.isVisible = isPeMonthsRequired
                if (!isPeMonthsRequired) {
                    paneUiData.peMonths.uiValue = paneUiData.peMonths.defaultValue
                }
                startWorkingButton.isDisable = paneUiData.anyRequiredDataDefault()
            }
        })
    }

    private fun initPeMonths() {
        peMonthsHBox.isVisible = paneUiData.peMonths.isRequired
        peMonthsTextField.addIntegerFormatter(regexFilter("[0-9]|1[01]"))
        peMonthsTextField.textProperty().addListener { _, old, new ->
            paneUiData.peMonths.uiValue = new.toIntOrNull() ?: paneUiData.peMonths.defaultValue
        }
        subscribe(PeMonthsNotifier.PE_MONTHS_TOPIC, object : PeMonthsNotifier {
            override fun accept(newPeMonths: Int) {
                peMonthsTextField.text = newPeMonths.toString()
                startWorkingButton.isDisable = paneUiData.anyRequiredDataDefault()
            }
        })
    }

//    private fun initDifficulty() {
////        Todo: make it autocomplete https://stackoverflow.com/questions/19924852/autocomplete-combobox-in-javafx
//        difficultyObservableList = FXCollections.observableList(paneUiData.difficulty.dataList)
//        difficultyComboBox.items = difficultyObservableList
//
//        val cellFactory = Callback<ListView<Country>, ListCell<Country>> {
//            object : ListCell<Country>() {
//                override fun updateItem(item: Country?, empty: Boolean) {
//                    super.updateItem(item, empty)
//                    if (item == null || empty) {
//                        graphic = null;
//                    } else {
//                        text = item.translation.getOrDefault(LanguagePaneUiData.language.currentValue, "")
//                    }
//                }
//            }
//        }
//
//        difficultyComboBox.buttonCell = cellFactory.call(null)
//        difficultyComboBox.cellFactory = cellFactory
//
//        difficultyComboBox.selectionModel.selectedItemProperty().addListener { _ ->
//            paneUiData.difficulty.uiValue = difficultyComboBox.selectionModel.selectedIndex
//        }
//        subscribe(DifficultyNotifier.DIFFICULTY_TOPIC, object : DifficultyNotifier {
//            override fun accept(newCountryIndex: Int) {
//                difficultyComboBox.selectionModel.select(newCountryIndex)
//                startWorkingButton.isDisable = paneUiData.anyRequiredDataDefault()
//            }
//        })
//
//        subscribe(CountryComparatorNotifier.COUNTRY_COMPARATOR_TOPIC, object : CountryComparatorNotifier {
//            override fun accept(newComparator: Comparator<Country>) {
//                difficultyComboBox.items = difficultyObservableList.sorted(newComparator)
//            }
//        })
//    }

//    private fun initProgrammingLanguage() {
//        programmingLanguageComboBox.items = FXCollections.observableList(paneUiData.programmingLanguage.dataList.map { it.key })
//
//        programmingLanguageComboBox.selectionModel.selectedItemProperty().addListener { _ ->
//            paneUiData.programmingLanguage.uiValue = programmingLanguageComboBox.selectionModel.selectedIndex
//        }
//        subscribe(ProgrammingLanguageNotifier.PROGRAMMING_LANGUAGE_TOPIC, object : ProgrammingLanguageNotifier {
//            override fun accept(newLanguageIndex: Int) {
//                programmingLanguageComboBox.selectionModel.select(newLanguageIndex)
//                startWorkingButton.isDisable = paneUiData.anyRequiredDataDefault()
//            }
//        })
//    }

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
                val newLanguage = LanguagePaneUiData.language.dataList[newLanguageIndex]
                val surveyPaneText = translations?.get(newLanguage)
                surveyPaneText?.let {
                    programLabel.text = it.program
                    yearLabel.text = it.year
                    experienceLabel.text = it.experience
                    peYearsLabel.text = it.years
                    peMonthsLabel.text = it.months
//                    difficultyLabel.text = it.difficulty
                    startWorkingText.text = it.startSession
//                    programmingLanguageLabel.text = it.programmingLanguage
//                    paneUiData.difficulty.dataListComparator =
//                        compareBy { c -> c.translation.getOrDefault(newLanguage, "") }
                }
                yearRadioButtons.zip(paneUiData.year.dataList) { rb, g ->
                    rb.text = g.translation[newLanguage] ?: ""
                }
            }
        })
    }
}