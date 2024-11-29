// Copyright (c) 2020 Anastasiia Birillo

const capitalizeFirstLetter = (string) => {
  return string.charAt(0).toUpperCase() + string.toLowerCase().slice(1);
};

const getAlreadyTakenError = (object) => {
  return {
    content: {
      error: {
        key: `${object.toUpperCase()}_ALREADY_EXISTS`,
        description: `${capitalizeFirstLetter(object)} already taken.`,
        message: 'Validation failed.'
      }
    },
    code: 406
  }
};

const getNotExistsError = (object) => {
  return {
    content: {
      error: {
        key: `${object.toUpperCase()}_NOT_EXISTS`,
        description: `${capitalizeFirstLetter(object)} does not exists.`,
        message: 'Validation failed.'
      }
    },
    code: 406
  }
};

const ERRORS = {
  VALIDATION: {
    DATA_ITEM: {
      ALREADY_TAKEN: getAlreadyTakenError('DATA_ITEM'),
      NOT_EXISTS: getNotExistsError('DATA_ITEM'),
    },
    HINT_ITEM: {
      ALREADY_TAKEN: getAlreadyTakenError('HINT_ITEM'),
      NOT_EXISTS: getNotExistsError('HINT_ITEM'),
    },
    USER: {
      ALREADY_TAKEN: getAlreadyTakenError('USER'),
      NOT_EXISTS: getNotExistsError('USER'),
      DATA: {
        ALREADY_TAKEN: getAlreadyTakenError('USER_DATA'),
      }
    },
    TASK: {
      ALREADY_TAKEN: getAlreadyTakenError('TASK'),
      NOT_EXISTS: getNotExistsError('TASK'),
    },
    DIALOG_TEXT: {
      ALREADY_TAKEN: getAlreadyTakenError('DIALOG_TEXT'),
      NOT_EXISTS: getNotExistsError('DIALOG_TEXT'),
    },
    FILE: {
      NOT_RECEIVED: {
        content: {
          error: {
            key: 'FILE_NOT_RECEIVED',
            description: 'File is not received.',
            message: 'Validation failed.'
          }
        },
        code: 406
      }
    },
    ACTIVITY_TRACKER_ITEM: {
      ALREADY_TAKEN: getAlreadyTakenError('ACTIVITY_TRACKER_ITEM'),
      NOT_EXISTS: getNotExistsError('ACTIVITY_TRACKER_ITEM'),
    },
    SETTINGS: {
      NOT_EXISTS: getNotExistsError('SETTINGS'),
      ALREADY_TAKEN: getAlreadyTakenError('SETTINGS'),
    },
    GENDER: {
      NOT_EXISTS: getNotExistsError('GENDER'),
      ALREADY_TAKEN: getAlreadyTakenError('GENDER'),
      MAX_LIMIT: {
        content: {
          error: {
            key: 'GENDER_MAX_LIMIT',
            description: 'Number of Gender values reached the maximum value.',
            message: 'Validation failed.'
          }
        },
        code: 406
      }
    },
    COUNTRY: {
      NOT_EXISTS: getNotExistsError('COUNTRY'),
      ALREADY_TAKEN: getAlreadyTakenError('COUNTRY'),
    },
    EXPERIENCE: {
      NOT_EXISTS: getNotExistsError('EXPERIENCE'),
      ALREADY_TAKEN: getAlreadyTakenError('EXPERIENCE'),
    }
  },
  INTERNAL_SERVER: {
    content: {
      error: {
        key: 'INTERNAL_SERVER_ERROR',
        description: 'An internal server error ouccured.',
        message: 'Internal server error.'
      }
    },
    code: 500
  }
};

module.exports = {
  ERRORS
};
