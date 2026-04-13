package org.jetbrains.research.tasktracker.tracking.logger

import com.intellij.openapi.util.io.FileUtil
import com.jetbrains.rd.util.AtomicInteger
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVPrinter
import org.jetbrains.research.tasktracker.config.MainTaskTrackerConfig
import java.io.File
import java.io.FileOutputStream
import java.io.OutputStreamWriter
import java.nio.charset.StandardCharsets

abstract class BaseLogger {
    /**
     * filename without extension
     */
    abstract val logPrinterFilename: String
    abstract val loggedData: LoggedData<*, *>

    private val logPrinters = mutableListOf<LogPrinter>()
    private val atomicInteger = AtomicInteger(0)
    private val lock = Any()

    protected fun log(dataToPrint: Iterable<*>) {
        val logPrinter = getActiveLogPrinter()
        // Writing to a plain file via CSVPrinter does not require IDE write action; just ensure thread-safety.
        synchronized(lock) {
            logPrinter.csvPrinter.printRecord(dataToPrint)
        }
    }

    /**
     * Gets the active logPrinter or creates a new one if there was none or the active one was full
     */
    private fun getActiveLogPrinter(): LogPrinter = synchronized(lock) {
        val activePrinter = getLastPrinter()
        if (activePrinter.isFull()) {
            addLogPrinter()
        } else {
            activePrinter
        }
    }

    private fun getLastPrinter(): LogPrinter = synchronized(lock) {
        if (logPrinters.isEmpty()) {
            addLogPrinter()
        } else {
            logPrinters.last()
        }
    }

    private fun addLogPrinter(): LogPrinter = synchronized(lock) {
        val logFile = createLogFile("${logPrinterFilename}${atomicInteger.getAndIncrement()}.csv")
        val fileWriter = OutputStreamWriter(FileOutputStream(logFile), StandardCharsets.UTF_8)
        val csvPrinter = CSVPrinter(fileWriter, CSVFormat.DEFAULT)
        csvPrinter.printRecord(loggedData.headers)
        logPrinters.add(LogPrinter(csvPrinter, fileWriter, logFile))
        logPrinters.last()
    }

    private fun createLogFile(fileName: String): File {
        val logDir = File(MainTaskTrackerConfig.logFilesFolder)
        if (!logDir.exists()) {
            logDir.mkdirs()
        }
        val logFile = File("${MainTaskTrackerConfig.logFilesFolder}/$fileName")
        FileUtil.createIfDoesntExist(logFile)
        return logFile
    }

    fun getLogFiles(): List<File> = synchronized(lock) {
        logPrinters.map {
            it.csvPrinter.flush()
            it.logFile
        }
    }
}