/*
Direct Marketing Agriculture - Updated Database
Compatible with Flask Order + Offer Logic
MariaDB / MySQL
*/

CREATE DATABASE IF NOT EXISTS `directmarketingagriculture`
DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;

USE `directmarketingagriculture`;

SET FOREIGN_KEY_CHECKS=0;

/* ===================== BUYERS ===================== */

DROP TABLE IF EXISTS `buyers`;
CREATE TABLE `buyers` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `bname` varchar(200),
  `bemail` varchar(200),
  `password` varchar(200),
  `contact` varchar(200),
  `address` varchar(200),
  `profile` varchar(200),
  `status` varchar(200) DEFAULT 'pending',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

/* ===================== SELLERS ===================== */

DROP TABLE IF EXISTS `sellers`;
CREATE TABLE `sellers` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `sname` varchar(200),
  `semail` varchar(200),
  `password` varchar(200),
  `contact` varchar(200),
  `address` varchar(200),
  `profile` varchar(200),
  `status` varchar(200) DEFAULT 'pending',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

/* ===================== CROP INFO ===================== */

DROP TABLE IF EXISTS `cropinfo`;
CREATE TABLE `cropinfo` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `cropname` varchar(200),
  `category` varchar(200),
  `Minimumcost` varchar(200),
  `myfile` varchar(200),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

/* ===================== CROP PRICE (SELLER CROPS + OFFERS) ===================== */

DROP TABLE IF EXISTS `cropprice`;
CREATE TABLE `cropprice` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `cropname` varchar(200),
  `category` varchar(200),
  `mincost` varchar(200),
  `quantity` varchar(200),
  `Yieldtime` varchar(200),
  `myfile` varchar(200),
  `semail` varchar(200),
  `address` varchar(200),
  `amount` varchar(200),
  `status` varchar(200) DEFAULT 'pending',
  `totalquantity` varchar(200),

  /* QR + OFFER SUPPORT */
  `qr_path` varchar(255),
  `discount_percentage` float DEFAULT 0,
  `offer_start_date` date,
  `offer_end_date` date,
  `original_price` float,

  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

/* ===================== CROP ORDER (BUYER ORDERS) ===================== */

DROP TABLE IF EXISTS `croporder`;
CREATE TABLE `croporder` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `cropname` varchar(200),
  `category` varchar(200),
  `mincost` varchar(200),
  `quantity` varchar(200),
  `myorder` varchar(200),
  `season` varchar(200),
  `totalquantity` varchar(200),
  `semail` varchar(200),
  `bemail` varchar(200),
  `amount` varchar(200),
  `status` varchar(200) DEFAULT 'pending',
  `imgfile` varchar(200),

  /* DISCOUNT SUPPORT */
  `discount_amount` float DEFAULT 0,
  `final_amount` float,
  `applied_discount` float DEFAULT 0,

  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

/* ===================== PAYMENT ===================== */

DROP TABLE IF EXISTS `payment`;
CREATE TABLE `payment` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `Amount` varchar(200),
  `Cardname` varchar(200),
  `Cardnumber` varchar(100),
  `expmonth` varchar(200),
  `cvv` varchar(200),
  `Email` varchar(200),
  `semail` varchar(200),
  `status` varchar(200) DEFAULT 'pending',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

SET FOREIGN_KEY_CHECKS=1;
