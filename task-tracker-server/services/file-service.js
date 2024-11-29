// Copyright (c) 2020 Anastasiia Birillo

const fs = require('fs');
const zipFolder = require('zip-folder');

// If the directory is exist -> delete it and create new one
const initDirectory = (path) => {
    if (fs.existsSync(path)) {
        deleteDirectory(path);
    }
    fs.mkdirSync(path);
};

// If the directory is not exist -> create it
const createDirectory = (path) => {
    if (!fs.existsSync(path)) {
        fs.mkdirSync(path);
    }
};

const deleteFile = (path) => {
    return new Promise((resolve, reject) => {
        fs.unlink(path, (err) => {
            if (err) {
                reject(err);
            } else {
                resolve();
            }
        });
    });
};

const deleteDirectory = (path) => {
    fs.readdirSync(path).forEach(function (file, index) {
        const curPath = path + '/' + file;
        if (fs.lstatSync(curPath).isDirectory()) {
            deleteDirectory(curPath);
        } else {
            fs.unlinkSync(curPath);
        }
    });
    fs.rmdirSync(path);
};

const copyFile = (sourcePath, destinationPath) => {
    return new Promise((resolve, reject) => {
        try {
            fs.copyFile(sourcePath, destinationPath, (err) => {
                if (err) {
                    resolve(false);
                } else {
                    resolve(true);
                }
            });
        } catch (e) {
            resolve(false);
        }
    });
};

// Todo: send path without waiting
const createArchive = async (path) => {
    initDirectory('./download');
    return new Promise((resolve, reject) => {
        zipFolder(path, './download/data.zip', function (err) {
            if (err) {
                resolve(null);
            } else {
                resolve('/download/data.zip');
            }
        });

    });
};

module.exports = {
    copyFile,
    deleteFile,
    deleteDirectory,
    createArchive,
    initDirectory,
    createDirectory,
};
