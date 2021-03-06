import os
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from UI.ui import Ui_MainWindow
from stimulus.stimulus import *
from experiment.experiment import *


class MainWindow(QMainWindow, Ui_MainWindow, QWidget):
    """
    User interface component that serves as central navigating point in the application.
    Lets user conduct and edit experiments and stimulus profiles
    """
    def __init__(self, settings_dialog, analysis_dialog, running_experiment_dialog, serial_interface, size, camera,
                 stimulus_path="stimulus/stimulus_profiles/",
                 experiments_path="experiment/experiment_profiles/",
                 video_path="experiment/videos/",
                 logs_path="experiment/logs/"):
        """

        :param settings_dialog: Instance of SettingsDialog.py
        :param analysis_dialog: Instance of AnalysisDialog.py
        :param running_experiment_dialog: Instance of RunningExperimentDialog.py
        :param serial_interface: Instance of serial_interface.py
        :param size: tuple (int : width, int : height) of window
        :param camera: instance of camera.py
        :param stimulus_path: string indicating path to load stimulus profiles from
        :param experiments_path: string indicating path to load experiment profiles from
        :param video_path: string indicating path to load videos from
        :param logs_path: string indicating path to load logs from (NOT IN USE)
        """

        super().__init__()
        self.setupUi(self)
        self.analysis_dialog = analysis_dialog
        self.settings_dialog = settings_dialog

        """Init Camera and Video Settings"""
        self.video_path = video_path
        self.video_name = ""
        self.line_edit_video_path.setText(video_path)
        self.btn_set_video_path.clicked.connect(self.set_video_path)

        self.camera = camera
        self.camera.cam_connected_signal.connect(self.show_camera_status)
        self.camera.emit_cam_status()

        """Init Run Settings"""
        self.thread_pool = QThreadPool()
        self.serial_interface = serial_interface

        """Initialize Experiment Settings"""
        self.experiments_path = experiments_path
        self.show_experiment_profile_names()
        self.current_experiment = None
        self.list_exp_profiles.itemDoubleClicked.connect(self.add_experiment_to_run)

        self.list_experiments_to_run.itemClicked.connect(self.view_experiment_to_run)

        self.experiment_in_progress = False

        self.logs_path = logs_path
        self.line_edit_logs_path.setText(logs_path)
        self.btn_set_logs_path.clicked.connect(self.set_logs_path)
        # self.format_duration_text()
        self.set_duration_display(self.spin_duration_hour.value(), self.spin_duration_min.value(),
                                  self.spin_duration_sec.value())

        self.spin_duration_hour.valueChanged.connect(self.format_duration_text)
        self.spin_duration_min.valueChanged.connect(self.format_duration_text)
        self.spin_duration_sec.valueChanged.connect(self.format_duration_text)

        self.btn_run.clicked.connect(self.run_experiment)

        self.running_experiment_dialog = running_experiment_dialog
        self.running_experiment_dialog.buttonBox.accepted.connect(self.abort_experiment_run)
        # Init Additional Settings
        self.date_time_hatching.setDateTime(QDateTime.currentDateTime())

        """Initialize Stimulus Settings"""
        # Bind menu actions
        self.actionSetup.triggered.connect(self.settings_dialog.show)
        self.actionView.triggered.connect(analysis_dialog.show)
        self.actionExperiment_save.triggered.connect(self.save_experiment)
        self.actionExperiment_open.triggered.connect(self.open_experiment)
        self.actionStimulus_Profile_save.triggered.connect(self.save_stimulus_profile)

        # Init Stimulus Profile and Data
        self.stimulus_path = stimulus_path
        self.current_stimulus_profile = None
        self.current_stimulus_profile_name = None
        self.show_stimulus_profile_names()
        self.stimulus_plotted_data = []
        self.deleted_plot_items = []
        self.center_stimulus_plot()

        # Bindings Stimulus List
        self.list_stim_profiles.itemDoubleClicked.connect(self.view_stimulus_profile)

        # Bindings Stimulus UI
        self.btn_clear_plot.clicked.connect(self.clear_plot)
        self.btn_center_graph.clicked.connect(self.center_stimulus_plot)
        self.btn_add_stim.clicked.connect(self.add_to_stimulus_plot)
        self.btn_reset_stim.clicked.connect(self.reset_spin_and_slider)
        # self.line_edit_stimulus_name.returnPressed.connect(self.test)
        # self.btn_save_stim_profile.clicked.connect(save_stimulus_profile(self.stimulus_plot_data), self)

        self.hslider_stim_led_start.valueChanged.connect(self.slide_adjust_led_start)
        self.spin_stim_led_start.valueChanged.connect(self.spin_adjust_led_start)
        self.hslider_stim_led_end.valueChanged.connect(self.slide_adjust_led_end)
        self.spin_stim_led_end.valueChanged.connect(self.spin_adjust_led_end)

        # Bindings Stimulus Plot
        self.stim_profile_plot.sceneObj.sigMouseClicked.connect(self.stimulus_plot_clicked)
        # self.stim_profile_plot.setXRange(0, 100, 0)
        # self.stim_profile_plot.setYRange(0, 100, 0)

        # Bind keyboard shortcuts
        self.shortcut_undo = QShortcut(QKeySequence("Ctrl+z"), self)
        self.shortcut_redo = QShortcut(QKeySequence("Ctrl+y"), self)
        self.shortcut_save = QShortcut(QKeySequence("Ctrl+s"), self)
        self.shortcut_save_stimulus_profile = QShortcut(QKeySequence("Ctrl+shift+s"), self)
        self.shortcut_open = QShortcut(QKeySequence("Ctrl+o"), self)
        self.shortcut_open_stimulus_profile = QShortcut(QKeySequence("Ctrl+shift+o"), self)
        self.shortcut_delete = QShortcut(QKeySequence("delete"), self)
        self.shortcut_refresh = QShortcut(QKeySequence("F5"), self)

        self.shortcut_undo.activated.connect(self.undo)
        self.shortcut_redo.activated.connect(self.redo)
        self.shortcut_save.activated.connect(self.save_experiment)
        self.shortcut_save_stimulus_profile.activated.connect(self.save_stimulus_profile)
        self.shortcut_refresh.activated.connect(self.refresh_items)

        # self.resize(size.width(), size.height())
        # self.showFullScreen()
        self.tabWidget.setCurrentIndex(0)
        self.showMaximized()

    def show_camera_status(self, status):
        """
        Display if camera is connected or not
        :param status: bool indicating if connected, true is connected
        :return:
        """
        if status:
            self.label_status_value.setText("Connected")
            self.label_status_value.setStyleSheet("QLabel { color : green }")
        else:
            self.label_status_value.setText("Not Connected")
            self.label_status_value.setStyleSheet("QLabel { color : red }")

    def set_logs_path(self):
        """
        THIS METHOD IS A DUD. Can be expanded upon in future development
        Set logs path.
        :return: None
        """
        path = QFileDialog.getExistingDirectory(dir=self.video_path, caption="Set Path to Logs")

    def refresh_items(self):
        """
        Update list showing of experiment and stimulus profiles
        :return: None
        """
        self.show_experiment_profile_names()
        self.show_stimulus_profile_names()

    def undo(self):
        """
        Reverts the last change made to the stimulus plot.
        :return: None
        """
        deleted = self.stimulus_plotted_data.pop()
        self.deleted_plot_items.append(deleted)
        self.plot_stimulus_data()
        if len(self.stimulus_plotted_data) == 0:
            self.set_duration_display(00, 00, 00)
        else:
            d = self.convert_to_duration(self.stimulus_plotted_data[-1]["time"][1])
            self.set_duration_display(d["h"], d["m"], d["s"])

    def redo(self):
        """
        Reapplies the last removal from the stimulus plot
        :return: None
        """
        undeleted = self.deleted_plot_items.pop()
        self.stimulus_plotted_data.append(undeleted)
        self.plot_stimulus_data()
        d = self.convert_to_duration(undeleted["time"][1])
        self.set_duration_display(d["h"], d["m"], d["s"])

    def save_stimulus_profile(self):
        """
        Saves the currently stored stimulus data to a profile
        :return: None
        """
        file = QFileDialog.getSaveFileName(self, dir=self.stimulus_path, filter="*.json",
                                           caption="Save Stimulus Profile")

        file_name = file[0][file[0].rfind('/') + 1: len(file[0])].split('.')[0]
        if file_name != '':
            profile = make_stimulus_profile(self.stimulus_plotted_data, file_name=file_name)
            save_stimulus_profile(profile)
            self.current_stimulus_profile_name = file_name
            self.label_stim_profile_name.setText(file_name)
            self.current_stimulus_profile = profile
        self.show_stimulus_profile_names()

    def open_experiment(self):
        """
        THIS METHOD IS A DUD. Can be expanded upon in future development
        Open experiments via the action menu
        :return: None
        """
        experiment = QFileDialog.getOpenFileName(self, dir="experiment/experiment_profiles/", filter="*.json")

    def save_experiment(self):
        """
        Save experiment profile via a dialog
        :return: None
        """
        if self.current_stimulus_profile is None:
            self.current_stimulus_profile = make_stimulus_profile(self.stimulus_plotted_data)
        experiment = QFileDialog.getSaveFileName(self, dir=self.experiments_path, filter="*.json",
                                                 caption="Save Experiment")
        file_name = experiment[0][experiment[0].rfind('/') + 1: len(experiment[0])].split('.')[0]
        if file_name != '':
            self.video_name = file_name + ".avi"
            save_experiment_profile(stimulus_profile=self.current_stimulus_profile, file_name=file_name,
                                    experiment_settings=self.get_current_experiment_settings())

        self.show_stimulus_profile_names()
        self.show_experiment_profile_names()

    def show_experiment_profile_names(self):
        """
        Brings up all experiment profile names
        :return: None
        """
        self.list_exp_profiles.clear()
        for e in get_all_experiment_profile_names():
            self.list_exp_profiles.addItem(e)

    def add_experiment_to_run(self):
        """
        Adds an experiment to the list of experiments to run
        :return: None
        """
        selected_name = self.list_exp_profiles.selectedItems()[0].text()
        self.list_experiments_to_run.addItem(selected_name)

    def set_experiment_settings(self, settings):
        """
        Set experiment settings and fill out UI components accordingly
        :param settings: Comprehensive dictionary object containing experiment settings
        :return: None
        """
        self.spin_duration_hour.setValue(settings["duration"]["hours"])
        self.spin_duration_min.setValue(settings["duration"]["mins"])
        self.spin_duration_sec.setValue(settings["duration"]["secs"])
        self.format_duration_text()

        self.line_edit_video_path.setText(settings["video_path"])
        self.line_edit_logs_path.setText(settings["log_path"])
        self.checkbox_view_live.setChecked(settings["view_live"])
        self.checkbox_live_ir.setChecked(settings["view_infrared"])
        self.checkbox_dechorionated.setChecked(settings["dechorionated"])

        self.date_time_hatching.clear()
        self.date_time_hatching.setDateTime(QDateTime.fromString(settings["hatching_date_time"]))
        self.date_time_hatching.update()

        self.checkbox_genetics.setChecked(settings["genetics"])
        self.line_edit_geno_type.setText(settings["geno_type"])
        self.checkbox_drugs.setChecked(settings["drugs"])
        self.line_edit_drug_name.setText(settings["drug_name"])
        self.spin_crowdsize.setValue(settings["crowd_size"])

    def set_video_path(self):
        """
        Sets the current path to load or save videos to via a dialog
        :return: None
        """
        path = QFileDialog.getExistingDirectory(dir=self.video_path, caption="Set Path to Videos")
        if self.video_name is not None:
            if self.camera.set_video_path(path, self.video_name):
                self.video_path = path + "/"
                self.line_edit_video_path.setText(path + "/" + self.video_name)
        else:
            if self.camera.set_video_path(path):
                self.video_path = path + "/"
                self.line_edit_video_path.setText(path + "/")

    def set_video_path_no_dialog(self, path):
        """
        Sets the current path to load or save videos to without a dialog, useful for "behind-the-scenes" operations
        :param path: str with pathname
        :return: None
        """
        if self.video_name is not None:
            if self.camera.set_video_path(path, self.video_name):
                self.video_path = path
                self.line_edit_video_path.setText(path + "/" + self.video_name)

    def view_experiment_to_run(self):
        """
        Brings up experiment with associated settings and stimulus in the UI
        :return: None
        """
        selected = self.list_experiments_to_run.selectedItems()[0].text()
        experiment = load_experiment_profile(file_name=selected, file_path=self.experiments_path)
        if experiment is not None:
            self.current_experiment = experiment
            self.video_name = experiment["name"] + ".avi"
            self.set_video_path_no_dialog(self.video_path)
            # self.set_video_path()
            self.current_stimulus_profile = experiment["stimulus_profile"]
            self.stimulus_plotted_data = experiment["stimulus_profile"]["data"]
            self.current_stimulus_profile_name = self.current_stimulus_profile["name"]
            self.label_stim_profile_name.setText(self.current_stimulus_profile_name)

            self.set_experiment_settings(experiment["settings"])

            self.stim_profile_plot.clear()
            for d in self.stimulus_plotted_data:
                self.stim_profile_plot.plot(d["time"], d["value"])

            self.deleted_plot_items = []
            self.line_edit_video_path.setText(self.video_path + self.video_name)
            self.center_stimulus_plot()

    def view_stimulus_profile(self):
        """
        Brings up stimulus profile in plot and relevant UI slots, but keeps experiment settings
        :return: None
        """
        selected = self.list_stim_profiles.selectedItems()[0].text()
        profile = load_stimulus_profile(file_name=selected, file_path=self.stimulus_path)
        if profile is not None:
            self.label_stim_profile_name.setText(selected)
            self.stim_profile_plot.clear()
            self.current_stimulus_profile = profile

            data = profile["data"]
            for d in data:
                self.stim_profile_plot.plot(d["time"], d["value"])

            self.stimulus_plotted_data = profile["data"]
            # if self.get_total_duration() < profile["data"][-1]["time"][1]:
            d = self.convert_to_duration(profile["data"][-1]["time"][1])
            self.set_duration_display(d["h"], d["m"], d["s"])
            self.deleted_plot_items = []
            self.center_stimulus_plot()

    def grab_experiment_done_signal(self, done_signal):
        """
        Helper method to assist in handling events when experiment is complete
        :param done_signal: bool signal to indicate experiment is done
        :return:
        """
        self.experiment_in_progress = done_signal

    def run_experiment(self):
        """
        Validate conditions and run experiment is successful. Only one experiment can be run at a time.
        :return: None
        """
        if not self.experiment_in_progress and self.get_total_duration() != 0:
            self.experiment_in_progress = True
            self.runner = ExperimentRunner(plot_data=self.stimulus_plotted_data, duration=self.get_total_duration(),
                                           serial_interface=self.serial_interface, camera=self.camera,
                                           recording_experiment=self.checkbox_save_video.isChecked())

            self.runner.signal_experiment_in_progress.connect(lambda x: self.grab_experiment_done_signal(x))
            if self.checkbox_view_live.isChecked():
                self.settings_dialog.show()
            self.runner.run()
            self.running_experiment_dialog.reset()
            self.running_experiment_dialog.set_progress_increment(self.get_total_duration())
            self.running_experiment_dialog.rejected.connect(self.abort_experiment_run)
            self.running_experiment_dialog.signal_user_aborted_experiment.connect(self.abort_experiment_run)

            self.runner.signal_updating.connect(self.running_experiment_dialog.update_progress)
            self.runner.signal_experiment_done.connect(self.running_experiment_dialog.set_progress_completed)
            self.running_experiment_dialog.show()

        else:
            print("Experiment already in progress")

    def abort_experiment_run(self):
        """
        Stops the current experiment, any data recorded meanwhile is NOT destroyed.
        :return: None
        """
        self.running_experiment_dialog.reset()
        self.runner.abort_flag = True
        self.experiment_in_progress = False

    def show_stimulus_profile_names(self):
        """
        Brings up names of stimulus profiles from the stimulus profiles path
        :return: None
        """
        self.list_stim_profiles.clear()
        for n in get_all_stimulus_profile_names():
            self.list_stim_profiles.addItem(n)

        self.list_stim_profiles.sortItems()

    def reset_spin_and_slider(self):
        """
        Reset spinboxes and sliders used to add to stimulus plot
        :return: None
        """
        self.spin_start_secs.setValue(0)
        self.spin_start_mins.setValue(0)
        self.spin_start_hours.setValue(0)

        self.spin_end_secs.setValue(0)
        self.spin_end_mins.setValue(0)
        self.spin_end_hours.setValue(0)

        self.hslider_stim_led_end.setValue(0)
        self.hslider_stim_led_start.setValue(0)

    def plot_stimulus_data(self):
        """
        Insert stimulus data into the pyqtpragh plot
        :return: None
        """
        self.stim_profile_plot.clear()
        for p in self.stimulus_plotted_data:
            self.stim_profile_plot.plot(p["time"], p["value"])

    def get_hatching_date_time(self):
        """
        :return: String of datetime object assoicated with hatching
        """
        return self.date_time_hatching.dateTime().toString()

    def get_current_experiment_settings(self):
        """
        Collects all experiment settings and returns in comprehensive dictionary. Used when writing to experiment profile.
        :return: Dictionary with settings
        """
        return {"duration": self.get_duration_as_dict(), "video_path": self.video_path + self.video_name,
                "log_path": self.line_edit_logs_path.text(), "view_live": self.checkbox_view_live.isChecked(),
                "view_infrared": self.checkbox_live_ir.isChecked(),
                "dechorionated": self.checkbox_dechorionated.isChecked(),
                "hatching_date_time": self.get_hatching_date_time(), "genetics": self.checkbox_genetics.isChecked(),
                "geno_type": self.line_edit_geno_type.text(), "drugs": self.checkbox_drugs.isChecked(),
                "drug_name": self.line_edit_drug_name.text(), "crowd_size": self.spin_crowdsize.value()}

    def format_duration_text(self):
        """
        Set label showing experiment duration to HH:MM:SS
        :return: None
        """
        h_val = self.spin_duration_hour.value()
        m_val = self.spin_duration_min.value()
        s_val = self.spin_duration_sec.value()

        h = "0" + str(h_val) if h_val < 10 else str(h_val)
        m = "0" + str(m_val) if m_val < 10 else str(m_val)
        s = "0" + str(s_val) if s_val < 10 else str(s_val)

        self.line_edit_duration.setText(h + ":" + m + ":" + s)

    def get_duration_as_dict(self):
        """
        :return: Duration as dictionary object of hours, mins and seconds
        """
        hours = self.spin_duration_hour.value()
        mins = self.spin_duration_min.value()
        secs = self.spin_duration_sec.value()

        return {"hours": hours, "mins": mins, "secs": secs}

    def set_duration_display(self, h_val, m_val, s_val):
        """
        Updates spinboxes to newest duration value
        :param h_val: hours value
        :param m_val: minutes value
        :param s_val: seconds value
        :return: None
        """
        h = "0" + str(h_val) if h_val < 10 else str(h_val)
        m = "0" + str(m_val) if m_val < 10 else str(m_val)
        s = "0" + str(s_val) if s_val < 10 else str(s_val)

        self.line_edit_duration.setText(h + ":" + m + ":" + s)

        self.spin_duration_hour.setValue(h_val)
        self.spin_duration_min.setValue(m_val)
        self.spin_duration_sec.setValue(s_val)

    def get_total_duration(self):
        """
        :return: Total experiment duration in seconds
        """
        h = self.spin_duration_hour.value()
        m = self.spin_duration_min.value()
        s = self.spin_duration_sec.value()

        return h * 60 * 60 + m * 60 + s

    def slide_adjust_led_end(self):
        """
        Event fired when adjusting slider of LED stimulus end value
        :return: None
        """
        slide_val = self.hslider_stim_led_end.value()
        self.spin_stim_led_end.setValue(slide_val)

        if self.checkbox_sync_led.isChecked():
            self.spin_stim_led_start.setValue(slide_val)
            self.hslider_stim_led_start.setValue(slide_val)

    def slide_adjust_led_start(self):
        """
        Event fired when adjusting slider of LED stimulus end value.
        :return:
        """
        slide_val = self.hslider_stim_led_start.value()
        if self.checkbox_start.isChecked():
            self.spin_stim_led_start.setValue(0)
            self.hslider_stim_led_start.setValue(0)
        elif self.checkbox_sync_led.isChecked():
            self.spin_stim_led_end.setValue(slide_val)
            self.hslider_stim_led_start.setValue(slide_val)
        else:
            self.spin_stim_led_start.setValue(slide_val)

    def spin_adjust_led_start(self):
        """
        Event fired when adjusting spin box of stimulus LED start
        :return: None
        """
        spin_val_start = self.spin_stim_led_start.value()
        self.hslider_stim_led_start.setValue(spin_val_start)
        if self.checkbox_sync_led.isChecked():
            spin_val_end = self.spin_stim_led_end.value()
            self.hslider_stim_led_end.setValue(spin_val_end)

    def spin_adjust_led_end(self):
        """
        Event fired when adjusting spin box of stimulus LED end
        :return: None
        """
        spin_val = self.spin_stim_led_end.value()
        self.hslider_stim_led_end.setValue(spin_val)
        if self.checkbox_sync_led.isChecked():
            self.spin_stim_led_start.setValue(spin_val)
            self.hslider_stim_led_start.setValue(spin_val)

    def get_stimulus_start(self):
        """
        :return: start time of stimulus interval in seconds
        """
        hours = self.spin_start_hours.value()
        mins = self.spin_start_mins.value()
        secs = self.spin_start_secs.value()

        return hours * 60 * 60 + mins * 60 + secs

    def get_stimulus_end(self):
        """
        :return: end time of stimulus interval in seconds
        """
        hours = self.spin_end_hours.value()
        mins = self.spin_end_mins.value()
        secs = self.spin_end_secs.value()

        return hours * 60 * 60 + mins * 60 + secs

    def add_to_stimulus_plot(self):
        """
        Add a stimulus interval to the plot. Performs a series of validations first, updates local storage of intervals
        after. Invalid plot items will fail silently.
        :return: None
        """
        new_plot_item_start = self.get_stimulus_start()
        new_plot_item_end = self.get_stimulus_end()
        led_val_start = self.spin_stim_led_start.value()
        led_val_end = self.spin_stim_led_end.value()

        if self.validate_plot(new_plot_item_start, new_plot_item_end):
            if len(self.stimulus_plotted_data) > 0:
                last_plot_item_end = self.stimulus_plotted_data[-1]["time"][1]
                if new_plot_item_start > last_plot_item_end:
                    blank_plot_item = {'time': [last_plot_item_end, new_plot_item_start], 'value': [0, 0]}
                    self.stimulus_plotted_data.append(blank_plot_item)
                    self.stim_profile_plot.plot(blank_plot_item["time"], blank_plot_item["value"])
            elif len(self.stimulus_plotted_data) == 0 and new_plot_item_start != 0:
                blank_plot_item = {'time': [0, new_plot_item_start], 'value': [0, 0]}
                self.stim_profile_plot.plot(blank_plot_item['time'], blank_plot_item['value'])
                self.stimulus_plotted_data.append(blank_plot_item)

            data = {"time": [new_plot_item_start, new_plot_item_end], "value": [led_val_start, led_val_end]}
            self.stimulus_plotted_data.append(data)
            self.stim_profile_plot.plot(data["time"], data["value"])
            d = self.convert_to_duration(new_plot_item_end)
            if new_plot_item_end > self.get_total_duration():
                self.set_duration_display(d["h"], d["m"], d["s"])
            self.center_stimulus_plot()

    def convert_to_duration(self, time_in_seconds):
        """
        Make dictionary of time values from seconds, useful for formating
        :param time_in_seconds: int
        :return: dict of the values
        """
        h = time_in_seconds // 60 // 60 % 60
        m = time_in_seconds // 60 % 60
        s = time_in_seconds % 60

        return {"h": h, "m": m, "s": s}

    def validate_plot(self, start, end):
        """
        Validation method to ensure that no illegal plots of stimulus items are added
        :param start: int time of interval start
        :param end: int time interval end
        :param led_start: int led intensity at start
        :param led_end: int led intensity at end
        :return: bool indicating success of valication, true is successful
        """
        if end <= start:
            return False

        interval = [start, end]

        if interval in self.stimulus_plotted_data:
            return False

        for d in self.stimulus_plotted_data:
            t = d["time"]
            if t[0] <= start < t[1] or t[0] <= end <= t[1]:
                return False

        return True

    def clear_plot(self):
        """
        Removes all stimulus intervals from the plot
        :return:
        """
        self.stim_profile_plot.clear()
        self.deleted_plot_items = self.deleted_plot_items + self.stimulus_plotted_data
        self.stimulus_plotted_data = []

    def stimulus_plot_clicked(self, mouse_click_event):
        """
        THIS METHOD IS A DUD. Can be expanded upon in future development.
        Event fired when plot is clicked, can serve as basis for drawing with the cursor.
        :param mouse_click_event: Qt event of mouse clicked.
        :return:
        """
        pass
        # print(mouse_click_event.pos().x())
        # print(mouse_click_event.pos().y())

    def center_stimulus_plot(self):
        """
        Zooms and adjusts the plot to contain all plotted intervals
        :return:
        """
        self.stim_profile_plot.setYRange(0, 100)
        if self.get_total_duration() > 0:
            self.stim_profile_plot.setXRange(0, self.get_total_duration())
        else:
            self.stim_profile_plot.setXRange(0, 1)

    def closeEvent(self, event):
        """
        Event fired when closing the window, used to ensure safe shutdown of all components and windows
        :param event: QCloseEvent
        :return: None
        """
        self.camera.stop_cam()
        self.camera.shutdown()
        self.analysis_dialog.shutdown_video_handler()
        time.sleep(1) # give components on separate threads time to complete, consider using wait() instead
        if self.camera.out is not None:
            self.camera.out.release()
        if self.camera.capture_device is not None:
            self.camera.capture_device.release()

        self.settings_dialog.close()
        self.analysis_dialog.close()
