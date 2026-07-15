-- ============================================================================
-- GMIT STUDENT ATTENDANCE PANEL — DATABASE SCHEMA (v3 — with Subjects & Sessions)
-- ============================================================================
-- This file creates the database and every table the Django app needs,
-- plus Django's internal bookkeeping rows (so Django considers all
-- migrations already "applied" and won't try to recreate these tables).
--
-- HOW TO USE THIS FILE:
--   1. Open MySQL Workbench and connect to your local MySQL server.
--   2. File -> Open SQL Script -> select this file (gmit_attendance_schema.sql)
--   3. Click the lightning bolt "Execute" icon to run the whole script.
--   4. Done — all tables now exist inside the `gmit_attendance_db` database.
--   5. In your project terminal, run: python manage.py migrate
--      (it will say "No migrations to apply" — that confirms success)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS gmit_attendance_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

USE gmit_attendance_db;

SET FOREIGN_KEY_CHECKS=0;

--


--
-- Table structure for table `attendance_attendance`
--

DROP TABLE IF EXISTS `attendance_attendance`;
CREATE TABLE `attendance_attendance` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `status` varchar(8) NOT NULL,
  `marked_at` datetime(6) NOT NULL,
  `marked_by_id` bigint DEFAULT NULL,
  `student_id` bigint NOT NULL,
  `subject_id` bigint DEFAULT NULL,
  `session_number` smallint unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `attendance_attendance_student_id_subject_id_da_0879c7a5_uniq` (`student_id`,`subject_id`,`date`,`session_number`),
  KEY `attendance_attendanc_marked_by_id_0698c76f_fk_attendanc` (`marked_by_id`),
  KEY `attendance_attendance_student_id_94863613` (`student_id`),
  KEY `attendance_attendanc_subject_id_624b6d52_fk_attendanc` (`subject_id`),
  CONSTRAINT `attendance_attendanc_marked_by_id_0698c76f_fk_attendanc` FOREIGN KEY (`marked_by_id`) REFERENCES `attendance_customuser` (`id`),
  CONSTRAINT `attendance_attendanc_student_id_94863613_fk_attendanc` FOREIGN KEY (`student_id`) REFERENCES `attendance_student` (`id`),
  CONSTRAINT `attendance_attendanc_subject_id_624b6d52_fk_attendanc` FOREIGN KEY (`subject_id`) REFERENCES `attendance_subject` (`id`),
  CONSTRAINT `attendance_attendance_chk_1` CHECK ((`session_number` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `attendance_customuser`
--

DROP TABLE IF EXISTS `attendance_customuser`;
CREATE TABLE `attendance_customuser` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `role` varchar(10) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `attendance_customuser_groups`
--

DROP TABLE IF EXISTS `attendance_customuser_groups`;
CREATE TABLE `attendance_customuser_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `customuser_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `attendance_customuser_gr_customuser_id_group_id_62c42087_uniq` (`customuser_id`,`group_id`),
  KEY `attendance_customuser_groups_group_id_c30506da_fk_auth_group_id` (`group_id`),
  CONSTRAINT `attendance_customuse_customuser_id_62b2d181_fk_attendanc` FOREIGN KEY (`customuser_id`) REFERENCES `attendance_customuser` (`id`),
  CONSTRAINT `attendance_customuser_groups_group_id_c30506da_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `attendance_customuser_user_permissions`
--

DROP TABLE IF EXISTS `attendance_customuser_user_permissions`;
CREATE TABLE `attendance_customuser_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `customuser_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `attendance_customuser_us_customuser_id_permission_2cb28748_uniq` (`customuser_id`,`permission_id`),
  KEY `attendance_customuse_permission_id_4514391f_fk_auth_perm` (`permission_id`),
  CONSTRAINT `attendance_customuse_customuser_id_45e246af_fk_attendanc` FOREIGN KEY (`customuser_id`) REFERENCES `attendance_customuser` (`id`),
  CONSTRAINT `attendance_customuse_permission_id_4514391f_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `attendance_student`
--

DROP TABLE IF EXISTS `attendance_student`;
CREATE TABLE `attendance_student` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `usn` varchar(20) NOT NULL,
  `name` varchar(150) NOT NULL,
  `branch` varchar(5) NOT NULL,
  `semester` int NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_account_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usn` (`usn`),
  UNIQUE KEY `attendance_student_usn_branch_semester_81a8e6ca_uniq` (`usn`,`branch`,`semester`),
  UNIQUE KEY `user_account_id` (`user_account_id`),
  CONSTRAINT `attendance_student_user_account_id_fc5ac472_fk_attendanc` FOREIGN KEY (`user_account_id`) REFERENCES `attendance_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `attendance_subject`
--

DROP TABLE IF EXISTS `attendance_subject`;
CREATE TABLE `attendance_subject` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  `code` varchar(20) NOT NULL,
  `branch` varchar(5) NOT NULL,
  `semester` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `attendance_subject_name_branch_semester_d31627bd_uniq` (`name`,`branch`,`semester`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `attendance_teacherassignment`
--

DROP TABLE IF EXISTS `attendance_teacherassignment`;
CREATE TABLE `attendance_teacherassignment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `branch` varchar(5) NOT NULL,
  `semester` int NOT NULL,
  `teacher_id` bigint NOT NULL,
  `subject_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `attendance_teacherassignment_teacher_id_subject_id_322ee540_uniq` (`teacher_id`,`subject_id`),
  KEY `attendance_teacherassignment_teacher_id_b8c32635` (`teacher_id`),
  KEY `attendance_teacheras_subject_id_f8c60fc3_fk_attendanc` (`subject_id`),
  CONSTRAINT `attendance_teacheras_subject_id_f8c60fc3_fk_attendanc` FOREIGN KEY (`subject_id`) REFERENCES `attendance_subject` (`id`),
  CONSTRAINT `attendance_teacheras_teacher_id_b8c32635_fk_attendanc` FOREIGN KEY (`teacher_id`) REFERENCES `attendance_teacherprofile` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `attendance_teacherprofile`
--

DROP TABLE IF EXISTS `attendance_teacherprofile`;
CREATE TABLE `attendance_teacherprofile` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `is_approved` tinyint(1) NOT NULL,
  `requested_on` datetime(6) NOT NULL,
  `approved_on` datetime(6) DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `attendance_teacherpr_user_id_b20ec71a_fk_attendanc` FOREIGN KEY (`user_id`) REFERENCES `attendance_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_attendance_customuser_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_attendance_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `attendance_customuser` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping routines for database 'gmit_attendance_db'
--


--


--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (1,'contenttypes','0001_initial','2026-07-15 10:29:12.848111'),(2,'contenttypes','0002_remove_content_type_name','2026-07-15 10:29:12.926827'),(3,'auth','0001_initial','2026-07-15 10:29:13.184672'),(4,'auth','0002_alter_permission_name_max_length','2026-07-15 10:29:13.229933'),(5,'auth','0003_alter_user_email_max_length','2026-07-15 10:29:13.237618'),(6,'auth','0004_alter_user_username_opts','2026-07-15 10:29:13.243808'),(7,'auth','0005_alter_user_last_login_null','2026-07-15 10:29:13.251210'),(8,'auth','0006_require_contenttypes_0002','2026-07-15 10:29:13.252995'),(9,'auth','0007_alter_validators_add_error_messages','2026-07-15 10:29:13.258501'),(10,'auth','0008_alter_user_username_max_length','2026-07-15 10:29:13.263098'),(11,'auth','0009_alter_user_last_name_max_length','2026-07-15 10:29:13.268291'),(12,'auth','0010_alter_group_name_max_length','2026-07-15 10:29:13.281029'),(13,'auth','0011_update_proxy_permissions','2026-07-15 10:29:13.288797'),(14,'auth','0012_alter_user_first_name_max_length','2026-07-15 10:29:13.295791'),(15,'attendance','0001_initial','2026-07-15 10:29:13.904721'),(16,'admin','0001_initial','2026-07-15 10:29:14.024040'),(17,'admin','0002_logentry_remove_auto_add','2026-07-15 10:29:14.035247'),(18,'admin','0003_logentry_add_action_flag_choices','2026-07-15 10:29:14.044436'),(19,'attendance','0002_subject_alter_attendance_unique_together_and_more','2026-07-15 10:29:14.348020'),(20,'attendance','0003_alter_attendance_options_and_more','2026-07-15 10:29:14.495242'),(21,'sessions','0001_initial','2026-07-15 10:29:14.529089');
UNLOCK TABLES;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (1,'admin','logentry'),(9,'attendance','attendance'),(6,'attendance','customuser'),(7,'attendance','student'),(11,'attendance','subject'),(10,'attendance','teacherassignment'),(8,'attendance','teacherprofile'),(3,'auth','group'),(2,'auth','permission'),(4,'contenttypes','contenttype'),(5,'sessions','session');
UNLOCK TABLES;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add user',6,'add_customuser'),(22,'Can change user',6,'change_customuser'),(23,'Can delete user',6,'delete_customuser'),(24,'Can view user',6,'view_customuser'),(25,'Can add student',7,'add_student'),(26,'Can change student',7,'change_student'),(27,'Can delete student',7,'delete_student'),(28,'Can view student',7,'view_student'),(29,'Can add teacher profile',8,'add_teacherprofile'),(30,'Can change teacher profile',8,'change_teacherprofile'),(31,'Can delete teacher profile',8,'delete_teacherprofile'),(32,'Can view teacher profile',8,'view_teacherprofile'),(33,'Can add attendance',9,'add_attendance'),(34,'Can change attendance',9,'change_attendance'),(35,'Can delete attendance',9,'delete_attendance'),(36,'Can view attendance',9,'view_attendance'),(37,'Can add teacher assignment',10,'add_teacherassignment'),(38,'Can change teacher assignment',10,'change_teacherassignment'),(39,'Can delete teacher assignment',10,'delete_teacherassignment'),(40,'Can view teacher assignment',10,'view_teacherassignment'),(41,'Can add subject',11,'add_subject'),(42,'Can change subject',11,'change_subject'),(43,'Can delete subject',11,'delete_subject'),(44,'Can view subject',11,'view_subject');
UNLOCK TABLES;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
UNLOCK TABLES;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
UNLOCK TABLES;



SET FOREIGN_KEY_CHECKS=1;

-- ============================================================================
-- Done. Next step: in your project folder run
--     python manage.py migrate
-- (it will say "No migrations to apply" if everything matches correctly)
-- Then run: python manage.py createsuperuser
-- ============================================================================
