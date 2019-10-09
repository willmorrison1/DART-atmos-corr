
# DART-atmos-corr

A place for code and tutorials for atmospheric correction of longwave
infrared camera imagery using the [Discrete Anisotropic Radiative
Transfer (DART)](http://www.cesbio.ups-tlse.fr/us/dart.html) model.

This repository is being constantly updated with [tutorials](tutorials)
and [code](code) to give readers of Morrison *et al.* (2019) (in press)
a hands-on guide to performing atmospheric and emissivity corrections
for longwave infrared camera imagery across complex terrain.

## Summary of atmospheric correction routine

The overall routine is summarised in the below flowchart. Click on a
flowchart element to be directed to the appropriate documentation (WIP).

    ## PhantomJS not found. You can install it with webshot::install_phantomjs(). If it is installed, please make sure the phantomjs executable can be found via the PATH variable.

<!--html_preserve-->

<div id="htmlwidget-386e0abd9c85f1888079" class="DiagrammeR html-widget" style="width:672px;height:480px;">

</div>

<script type="application/json" data-for="htmlwidget-386e0abd9c85f1888079">{"x":{"diagram":"\ngraph TB\n            A(Real world image)-->B(Configure Blender model world)\n            B-->C(Create multi line of sight image)\n            B-->D(Run DART atmosphere simulation)\n            C-->E\n            D-->E\n            E(Post process images)-->F(Band calculation and correction)\n            A-->F\n            F-->G(Analysis)\n            click A \"https://github.com/willmorrison1/DART-atmos-corr\" \"Real world image guide\"\n            click B \"https://github.com/willmorrison1/DART-atmos-corr\" \"Model world creation guide\"\n            click C \"https://github.com/willmorrison1/DART-atmos-corr\" \"Multi line of sight image creation guide\"\n            click D \"https://github.com/willmorrison1/DART-atmos-corr\" \"DART atmosphere simulation guide\"\n            click E \"https://github.com/willmorrison1/DART-atmos-corr\" \"Simulation post-processing guide\"\n            click F \"https://github.com/willmorrison1/DART-atmos-corr\" \"Band calculation and real world image correction guide\"\n            click G \"https://github.com/willmorrison1/DART-atmos-corr\" \"Image analysis guide\""},"evals":[],"jsHooks":[]}</script>

<!--/html_preserve-->

A software package has been developed to work with DART outputs: [daRt
for the R programming language](https://github.com/willmorrison1/daRt)
and complements the atmospheric correction processing and analysis. daRt
methods are being developed to simplify the atmospheric correction
process.

![DARTscene3D\_London\_Islington](readme/DARTscene3D_London_Islington.PNG)
*DART “Scene 3D” view of central London area (430 m x 430 m) used for
testing of DART atmospheric correction.*
