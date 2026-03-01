package org.jetbrains.research.tasktracker.ui.main.panel.models

import kotlinx.serialization.Serializable

@Serializable
data class AgreementChecker(val pin: String, val agreements: List<Agreement>) {

    fun allRequiredChecked() =
        pin.isNotBlank() && agreements.filter { it.required }.all { it.checked }
}

@Serializable
data class Agreement(val checked: Boolean, val text: String, val required: Boolean)
