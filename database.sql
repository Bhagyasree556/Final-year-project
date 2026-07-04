/*
SQLyog Enterprise - MySQL GUI v6.56
MySQL - 5.5.5-10.4.32-MariaDB : Database - directmarketingagriculture
*********************************************************************
*/


/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;

CREATE DATABASE /*!32312 IF NOT EXISTS*/`directmarketingagriculture` /*!40100 DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci */;

USE `directmarketingagriculture`;

/*Table structure for table `buyers` */

DROP TABLE IF EXISTS `buyers`;

CREATE TABLE `buyers` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `bname` varchar(200) DEFAULT NULL,
  `bemail` varchar(200) DEFAULT NULL,
  `password` varchar(200) DEFAULT NULL,
  `contact` varchar(200) DEFAULT NULL,
  `address` varchar(200) DEFAULT NULL,
  `profile` varchar(200) DEFAULT NULL,
  `status` varchar(200) DEFAULT 'pending',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

/*Data for the table `buyers` */

insert  into `buyers`(`id`,`bname`,`bemail`,`password`,`contact`,`address`,`profile`,`status`) values (1,'buyer','buyer@gmail.com','181478ad7869aed751fb556c11ed7a0b','9658745896','tpt','static/profiles/balaram_5Mt8CGB_vVeJEa6.png','pending'),(2,'ravi','ravi@gmail.com','ff2a5d1d2612dff7ab7749c1f6f142e0','7458965874','tpt','static/profiles/index-video.jpg','pending');

/*Table structure for table `cropinfo` */

DROP TABLE IF EXISTS `cropinfo`;

CREATE TABLE `cropinfo` (
  `id` int(200) NOT NULL AUTO_INCREMENT,
  `cropname` varchar(200) DEFAULT NULL,
  `category` varchar(200) DEFAULT NULL,
  `Minimumcost` varchar(200) DEFAULT NULL,
  `myfile` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

/*Data for the table `cropinfo` */

insert  into `cropinfo`(`id`,`cropname`,`category`,`Minimumcost`,`myfile`) values (1,'Rice','Grains','120','static/profiles/rice.jpg'),(2,'Wheat','Grains','150','static/profiles/wheat.jpg'),(3,'Cashews','Nuts','800','static/profiles/download.jpg'),(4,'Almonds','Nuts','750','static/profiles/burgur.jpg'),(5,'Mustard Seeds','Seeds','100','static/profiles/Lentils.jpg'),(6,'Flaxseeds','Seeds','200','static/profiles/Jowar.jpg');

/*Table structure for table `croporder` */

DROP TABLE IF EXISTS `croporder`;

CREATE TABLE `croporder` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `cropname` varchar(200) DEFAULT NULL,
  `category` varchar(200) DEFAULT NULL,
  `mincost` varchar(200) DEFAULT NULL,
  `quantity` varchar(200) DEFAULT NULL,
  `myorder` varchar(200) DEFAULT NULL,
  `season` varchar(200) DEFAULT NULL,
  `totalquantity` varchar(200) DEFAULT NULL,
  `semail` varchar(200) DEFAULT NULL,
  `bemail` varchar(200) DEFAULT NULL,
  `amount` varchar(200) DEFAULT NULL,
  `status` varchar(200) DEFAULT 'pending',
  `imgfile` varchar(200) DEFAULT NULL,
  `qr_code_path` varchar(200) DEFAULT NULL,
  `discount_amount` DECIMAL(10,2) DEFAULT 0,
  `final_amount` DECIMAL(10,2),
  `applied_discount` DECIMAL(5,2) DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

/*Data for the table `croporder` */

insert  into `croporder`(`id`,`cropname`,`category`,`mincost`,`quantity`,`myorder`,`season`,`totalquantity`,`semail`,`bemail`,`amount`,`status`,`imgfile`,`qr_code_path`,`discount_amount`,`final_amount`,`applied_discount`) values (1,'Rice','Grains','120','1000','500','2024-11-30','500','sellers@gmail.com','buyer@gmail.com','60000','scanned','static/profiles/rice.jpg','static/paymentqr/Rice_paymentqr.png',0,60000,0);

/*Table structure for table `cropprice` */

DROP TABLE IF EXISTS `cropprice`;

CREATE TABLE `cropprice` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `cropname` varchar(200) DEFAULT NULL,
  `category` varchar(200) DEFAULT NULL,
  `mincost` varchar(200) DEFAULT NULL,
  `quantity` varchar(200) DEFAULT NULL,
  `Yieldtime` varchar(200) DEFAULT NULL,
  `myfile` varchar(200) DEFAULT NULL,
  `semail` varchar(200) DEFAULT NULL,
  `address` varchar(200) DEFAULT NULL,
  `amount` varchar(200) DEFAULT NULL,
  `status` varchar(200) DEFAULT 'pending',
  `totalquantity` varchar(200) DEFAULT NULL,
  `qr_path` varchar(200) DEFAULT NULL,
  `discount_percentage` DECIMAL(5,2) DEFAULT 0,
  `offer_start_date` DATE,
  `offer_end_date` DATE,
  `original_price` DECIMAL(10,2),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

/*Data for the table `cropprice` */

insert  into `cropprice`(`id`,`cropname`,`category`,`mincost`,`quantity`,`Yieldtime`,`myfile`,`semail`,`address`,`amount`,`status`,`totalquantity`,`qr_path`,`discount_percentage`,`offer_start_date`,`offer_end_date`,`original_price`) values (1,'Rice','Grains','120','1000','2024-11-30','static/profiles/rice.jpg','sellers@gmail.com','Bangalore',NULL,'scanned','500','static/qr/Rice_qr.png',0,NULL,NULL,NULL),(2,'Cashews','Nuts','800','1500','2024-12-31','static/profiles/burgur.jpg','sellers@gmail.com','Bangalore',NULL,'scanned','1500','static/qr/Cashews_qr.png',0,NULL,NULL,NULL);

/*Table structure for table `payment` */

DROP TABLE IF EXISTS `payment`;

CREATE TABLE `payment` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `Amount` varchar(200) DEFAULT NULL,
  `Cardname` varchar(200) DEFAULT NULL,
  `Cardnumber` varchar(100) DEFAULT NULL,
  `expmonth` varchar(200) DEFAULT NULL,
  `cvv` varchar(200) DEFAULT NULL,
  `Email` varchar(200) DEFAULT NULL,
  `semail` varchar(200) DEFAULT NULL,
  `status` varchar(200) DEFAULT 'pending',
  `discount_given` DECIMAL(10,2) DEFAULT 0,
  `original_amount` DECIMAL(10,2),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

/*Data for the table `payment` */

insert  into `payment`(`id`,`Amount`,`Cardname`,`Cardnumber`,`expmonth`,`cvv`,`Email`,`semail`,`status`,`discount_given`,`original_amount`) values (1,'60000','sbi','8521478569874589','12/25','123','buyer@gmail.com','sellers@gmail.com','Completed',0,60000);

/*Table structure for table `sellers` */

DROP TABLE IF EXISTS `sellers`;

CREATE TABLE `sellers` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `sname` varchar(200) DEFAULT NULL,
  `semail` varchar(200) DEFAULT NULL,
  `password` varchar(200) DEFAULT NULL,
  `contact` varchar(200) DEFAULT NULL,
  `address` varchar(200) DEFAULT NULL,
  `Profile` varchar(200) DEFAULT NULL,
  `status` varchar(200) DEFAULT 'pending',
  `is_blocked` BOOLEAN DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

/*Data for the table `sellers` */

insert  into `sellers`(`id`,`sname`,`semail`,`password`,`contact`,`address`,`Profile`,`status`,`is_blocked`) values (1,'sellers','sellers@gmail.com','181478ad7869aed751fb556c11ed7a0b','7485478596','Bangalore','static/profiles/client.jpg','pending',FALSE);

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;


DROP TABLE IF EXISTS `reports`;

CREATE TABLE `reports` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `seller_email` varchar(200) NOT NULL,
  `buyer_email` varchar(200) NOT NULL,
  `product_name` varchar(200) NOT NULL,
  `amount_paid` varchar(200) DEFAULT NULL,
  `description` text NOT NULL,
  `report_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(50) DEFAULT 'pending',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;