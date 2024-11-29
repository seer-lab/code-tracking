// Copyright (c) 2020 Anastasiia Birillo

const mongoose = require("mongoose");

const SettingsDescription = mongoose.model("SettingsDescription");
const formatterService = require('../../services/formatter-service');

const formatSurveyPane = (settingsDescription) => {
    if (!settingsDescription.surveyPane) {
        return settingsDescription;
    }
    const forToLowerCase = ['startSession'];
    const allKeys = Object.keys(settingsDescription.surveyPane);
    const forToLowerCaseWithColon = formatterService.subtractArrays(allKeys, forToLowerCase);
    settingsDescription.surveyPane = formatterService.applyFormatter(settingsDescription.surveyPane,
        forToLowerCase,
        formatterService.toLowerCase);
    settingsDescription.surveyPane = formatterService.applyFormatter(settingsDescription.surveyPane,
        forToLowerCaseWithColon,
        formatterService.toLowerCaseWithColon);
    return settingsDescription
};

const formatTaskChoosingPane = (settingsDescription) => {
    if (!settingsDescription.taskChoosingPane) {
        return settingsDescription;
    }
    const forToLowerCase = ['finishSession', 'startSolving'];
    const forToLowerCaseWithColon = ['chooseTask'];
    settingsDescription.taskChoosingPane = formatterService.applyFormatter(settingsDescription.taskChoosingPane,
        forToLowerCase,
        formatterService.toLowerCase);
    settingsDescription.taskChoosingPane = formatterService.applyFormatter(settingsDescription.taskChoosingPane,
        forToLowerCaseWithColon,
        formatterService.toLowerCaseWithColon);
    return settingsDescription
};

const formatTaskSolvingPane = (settingsDescription) => {
    if (!settingsDescription.taskSolvingPane) {
        return settingsDescription;
    }
    const forToLowerCase = Object.keys(settingsDescription.taskSolvingPane);
    settingsDescription.taskSolvingPane = formatterService.applyFormatter(settingsDescription.taskSolvingPane,
        forToLowerCase,
        formatterService.toLowerCase);
    return settingsDescription
};

const formatFinalPane = (settingsDescription) => {
    if (!settingsDescription.finalPane) {
        return settingsDescription;
    }
    const forToLowerCase = Object.keys(settingsDescription.finalPane);
    settingsDescription.finalPane = formatterService.applyFormatter(settingsDescription.finalPane,
        forToLowerCase,
        formatterService.toLowerCase);
    return settingsDescription
};

const formatSuccessPane = (settingsDescription) => {
    if (!settingsDescription.successPane) {
        return settingsDescription;
    }
    const forToLowerCase = Object.keys(settingsDescription.successPane);
    settingsDescription.successPane = formatterService.applyFormatter(settingsDescription.successPane,
        forToLowerCase,
        formatterService.toLowerCase);
    return settingsDescription
};

const formatCommonText = (settingsDescription) => {
    if (!settingsDescription.commonText) {
        return settingsDescription;
    }
    const forToLowerCase = Object.keys(settingsDescription.commonText);
    settingsDescription.commonText = formatterService.applyFormatter(settingsDescription.commonText,
        forToLowerCase,
        formatterService.toLowerCase);
    return settingsDescription
};

const createSettingsDescription = async (settingsDescription) => {
    const formats = [formatSurveyPane, formatTaskChoosingPane, formatTaskSolvingPane, formatFinalPane,
        formatSuccessPane, formatCommonText];
    for(const format of formats) {
        settingsDescription = format(settingsDescription)
    }
    const sd = new SettingsDescription(settingsDescription);
    return await sd.save();
};

const deleteSettingsDescription = async (settingsDescription) => {
    return await settingsDescription.remove();
};

module.exports = {
    createSettingsDescription,
    deleteSettingsDescription,
};
