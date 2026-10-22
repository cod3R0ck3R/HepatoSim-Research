[![License](http://img.shields.io/:license-affero-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.en.html)

# Models of HSC dynamics during the development and reversion of fibrosis

## 3 models

**reactMFB-with-inactivation.ka** : Final model describing the behvior of HSC during the development and reversion of fibrosis

**reactMFB-wo-inactivation.ka** : Model where the reactivation MFB are eliminated only by apoptosis/senescence

**iHSC-reversion-to-qHSC.ka** : HSC_dynamics_model.ka where was add rules describing the reversion of iHSC toward qHSC

## Use

The simulation can be run using KaSim or KUI, which can be downloaded here: https://kappalanguage.org/download

The selected model file must be opened in the KUI and then run.

It can also be launched using dircly KaSim with the following command in the terminal:
```
KaSim selected_model.ka
```
