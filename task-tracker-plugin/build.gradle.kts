import com.github.jengelman.gradle.plugins.shadow.tasks.ShadowJar
import org.jetbrains.kotlin.gradle.tasks.KotlinCompile
import org.jetbrains.kotlin.gradle.dsl.JvmTarget
import org.jetbrains.kotlin.js.translate.context.Namer.kotlin

plugins {
    id("org.jetbrains.intellij.platform") version "2.1.0"
    java
    kotlin("jvm") version "2.0.20"
    kotlin("plugin.serialization") version "2.0.20"
    id("com.github.johnrengelman.shadow") version "7.1.2"
    id("org.openjfx.javafxplugin") version "0.0.13"
    id("com.gluonhq.client-gradle-plugin") version "0.1.42"
    id("org.jetbrains.dokka") version "1.8.10"
}

group = "org.jetbrains.research.ml.tasktracker"
version = "1.1"

repositories {
    maven(url = "https://www.jetbrains.com/intellij-repository/releases")
    maven(url = "https://packages.jetbrains.team/maven/p/ij/intellij-dependencies")
    maven(url = "https://nexus.gluonhq.com/nexus/content/repositories/releases/")
    maven(url = "https://jitpack.io")
    maven(url = "https://kotlin.bintray.com/kotlinx")
    maven(url = "https://dl.bintray.com/kotlin/kotlin-eap")

    mavenCentral()
    google()
    intellijPlatform {
        defaultRepositories()
    }
}

dependencies {
    implementation(kotlin("stdlib-jdk8"))
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.3.2")
    implementation("org.jetbrains.kotlin:kotlin-reflect:1.8.22")
    implementation("com.opencsv:opencsv:5.0")
    implementation("joda-time:joda-time:2.9.2")
    implementation("org.apache.commons:commons-csv:1.7")
    implementation("com.gluonhq:charm-glisten:6.0.1")
    implementation("com.google.code.gson:gson:2.8.5")
    implementation("com.squareup.okhttp3:okhttp:4.2.2")
    implementation("com.google.auto.service:auto-service:1.0-rc7")
    implementation("org.eclipse.mylyn.github:org.eclipse.egit.github.core:2.1.5")
    implementation("net.lingala.zip4j:zip4j:2.6.1")
    implementation("com.github.holgerbrandl:krangl:v0.13")
    implementation("com.beust:klaxon:5.5")
    implementation("org.openjfx:javafx-controls:21.0.4")
    implementation("org.openjfx:javafx-fxml:21.0.4")
    implementation("org.jetbrains.kotlin:kotlin-stdlib-jdk8")

    testImplementation("junit:junit:4.12")

    intellijPlatform {
        val ideVersion = System.getenv().getOrDefault("TASK_TRACKER_PYCHARM_VERSION", "2024.3.4")
        println("Using ide version: $ideVersion")
        create("PC", ideVersion) // 'PY' for PyCharm Professional, 'PC' for PyCharm Community
        instrumentationTools()
    }
}

intellijPlatform {
    pluginConfiguration {
        name = "task-tracker-plugin"
    }
}

javafx {
    version = "21.0.4" +
            ""
    modules("javafx.controls", "javafx.fxml", "javafx.swing")
    configuration = "compileOnly"
}

java {
    sourceCompatibility = JavaVersion.VERSION_21
}

tasks.named<org.jetbrains.intellij.platform.gradle.tasks.PatchPluginXmlTask>("patchPluginXml") {
    changeNotes.set("""
      Add change notes here.<br>
      <em>most HTML tags may be used</em>""")
}

tasks.withType<KotlinCompile> {
    compilerOptions {
        jvmTarget.set(JvmTarget.JVM_21)
    }
}

gluonClient {
    reflectionList = arrayListOf(
        "javafx.fxml.FXMLLoader",
        "com.gluon.hello.views.HelloPresenter",
        "javafx.scene.control.Button",
        "javafx.scene.control.Label"
    )
}

tasks.withType<ShadowJar> {
    project.logger.warn("Don't forget to:\n" +
            "- set your remote server as baseUrl in QueryExecutor class\n" +
            "- turn OFF org.jetbrains.research.ml.tasktracker.Plugin.testMode")
}

tasks.withType<Wrapper> {
    gradleVersion = "8.10"
}

tasks.register("assemblePlugin") {
    dependsOn("shadowJar", "buildPlugin")
}

tasks.named<org.jetbrains.intellij.platform.gradle.tasks.RunIdeTask>("runIde") {
    dependsOn("shadowJar", "buildPlugin")
    jvmArgs = listOf("-Xmx2048m")
}
