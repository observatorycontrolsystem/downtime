## 2.5.0
### 2026-05-08

* Added uptime API supporting setting whole or fractions of nights of uptime on insturment_types on telescopes. It uses the semesters API of the observation portal to set the rest of the semester to downtime if used on an empty semester. It merges in multiple uptimes set, and uptime nights can be removed as well. Uses rise-set to determine nighttime boundaries for setting uptimes using only a "day".

## 2.4.4
#### 2024-08-01

* Support for any authenticated user submitted to api
* Support for filtering by exact reason
* Updated all dependencies to latest

## 2.4.0
#### 2022-02-24

* Add in ocs-authentication library for the auth backend

## 2.3.3
#### 2021-06-17

* Add automatic documentation generation

## 2.3.2
#### 2021-04-15

* Add instrument_type as optional field for downtimes

## 2.3.1
#### 2021-04-09

* Update some dependencies

## 2.3.0
##### 2021-01-19

* Rename some model fields and add Django Rest Framework

## 2.2.2
##### 2020-08-14

* Add `create_downtime` management command

## 2.2
##### 2020-01-23

* Port to PostgreSQL.

## 2.1
##### 2020-01-23

* Upgrade Gunicorn to version 20.0.4

## 2.0.1
##### 2019-05-23

* Add 2019B RTI Downtime slots

## 2.0.0
##### 2019-02-20

* Update for Kubernetes

## 1.0.0
##### 2018-10-31

* Begin versioning
