function displayNbDistributions(n){
    let i;
    for (i = 1; i < nDistributionsMax; i++) {
        if (i < n) {
            document.getElementById("distribution"+i).style.display = "flex"
        } else {
            document.getElementById("distribution"+i).style.display = "none"
        }
    }
    $('#n_distributions_to_display').val(n)

    if (n>1){
        $('.distributionBox').css('border','grey 1px solid').css('border-radius','5px')

        $('.custom_domain_fields').css('display','none')

        $('#distribution99').css('display','flex')
    }
    else {
         $('.custom_domain_fields').css('display','auto')
        $('#distribution99').css('display','none')
    }
}
nDistributionsInitial = $('#n_distributions_to_display').val()
nDistributionsMax = 3
displayNbDistributions(nDistributionsInitial)
displayAddDistrButton()
displayMixtureComponentOptions()

$('.left_pane').css('max-height',maxHeightPerDistr+'px')
        .css('overflow-y','auto').css('overflow-x','hidden')

function displayMetalogExample(){
    distributionIndex = 0
    displayNbDistributions(1)

    distributionDiv = $('#distribution'+distributionIndex)

    distributionDiv.find('[fieldtype=nb_pairs_to_display_hidden_field]').css('display','none')

    distributionDiv.find('[fieldtype=nb_pairs_to_display_hidden_field]').attr('value', 3)
    distributionDiv.find('[fieldtype=family]').val('metalog')

    distributionDiv.find('[fieldtype=plot_custom_domain_bool]').attr('checked',true)
    displayConditionalFieldsByFieldType('plot_custom_domain_bool','plot_custom_domain_FromTo',distributionIndex)

    distributionDiv.find('[fieldtype=plot_custom_domain_FromTo] [fieldtype=From]').attr('value', -100)
    distributionDiv.find('[fieldtype=plot_custom_domain_FromTo] [fieldtype=To]').attr('value', 100)

    distributionDiv.find('[fieldtype=metalog_boundedness]').attr('checked',false)
    displayConditionalFieldsByClass('metalog_boundedness','metalog_bounds',distributionIndex)

    distributionDiv.find('[fieldtype=metalog_allow_numerical]').attr('checked',true)

    distributionDiv.find('.pair0 [fieldtype=P]').val(0.1)
    distributionDiv.find('.pair0 [fieldtype=Q]').val(-20)

    distributionDiv.find('.pair1 [fieldtype=P]').val(.5)
    distributionDiv.find('.pair1 [fieldtype=Q]').val(-1)

    distributionDiv.find('.pair2 [fieldtype=P]').val(.9)
    distributionDiv.find('.pair2 [fieldtype=Q]').val(50)

    submitForm()

}
function displayGenBetaExample(){
    distributionIndex = 0
    displayNbDistributions(1)

    distributionDiv = $("#distribution"+distributionIndex)

    distributionDiv.find('[fieldtype=nb_pairs_to_display_hidden_field]').val(3)

    distributionDiv.find('[fieldtype=family]').val('generalized_beta')


    distributionDiv.find('[fieldtype=plot_custom_domain_bool]').attr('checked',false)
    displayConditionalFieldsByFieldType('plot_custom_domain_bool','plot_custom_domain_FromTo',distributionIndex)

    distributionDiv.find('[fieldtype=generalized_beta_bounds] [fieldtype=From]').val(-6)
    distributionDiv.find('[fieldtype=generalized_beta_bounds] [fieldtype=To]').val(-1)



    distributionDiv.find('.pair0 [fieldtype=P]').val( .2)
    distributionDiv.find('.pair0 [fieldtype=Q]').val( -5.2)

    distributionDiv.find('.pair1 [fieldtype=P]').val(.5)
    distributionDiv.find('.pair1 [fieldtype=Q]').val(-4)

    distributionDiv.find('.pair2 [fieldtype=P]').val(.8)
    distributionDiv.find('.pair2 [fieldtype=Q]').val(-1.3)

    submitForm()

}
function submitForm(){
    document.getElementById("dataInputForm").submit()
}
function displayNbPairs(distributionIndex) {
    distributionDiv = $("#distribution"+distributionIndex)

    nb_pairs = distributionDiv.find('[fieldtype=nb_pairs_to_display_hidden_field]').val()
    max_pairs = 10;
    let i;
    for (i = 0; i < max_pairs; i++) {
        if (i < nb_pairs) {
            distributionDiv.find(' .pair'+i).css("display","block")
        } else {
            distributionDiv.find(' .pair'+i).css("display","none")
        }
    }
    displayAddPairsButton(distributionIndex)
}
for (let i = 0; i < nDistributionsInitial; i++) {
    displayNbPairs(i)
}


function displayConditionalFieldsByFieldType(checkBoxFieldType, fieldType, distributionIndex) {
    distributionDiv = $("#distribution"+distributionIndex)

    const checked = distributionDiv.find("[fieldtype="+checkBoxFieldType+"]").prop('checked')
    if (checked) {
        distributionDiv.find("[fieldtype="+fieldType+"]").css('display','flex')
        // as it happens, when we do by field type we always want a flexbox. A more general method would set a dictionary for this.
    }
    else {
        distributionDiv.find("[fieldtype="+fieldType+"]").css('display','none')
    }
}
function displayConditionalFieldsByClass(checkBoxFieldType, classStr, distributionIndex) {
    distributionDiv = $("#distribution"+distributionIndex)
    const checked = distributionDiv.find("[fieldtype="+checkBoxFieldType+"]").prop('checked')
    if (checked) {
        distributionDiv.find("."+classStr).css('display','block')
        // as it happens, when we do by class we always want a block. A more general method would set a dictionary for this.
    }
    else {
        distributionDiv.find("."+classStr).css('display','none')
    }
}

for (let i = 0; i < nDistributionsInitial; i++) {
    displayConditionalFieldsByClass('metalog_boundedness','metalog_bounds',i)
    displayConditionalFieldsByFieldType('plot_custom_domain_bool','plot_custom_domain_FromTo',i)
}
displayConditionalFieldsByFieldType('mixture_domain_for_plot_bool','mixture_domain_for_plot_FromTo','99')

function displayDistributionSpecificOptions(distributionIndex) {
    distributionDiv = $("#distribution"+distributionIndex)

    const family = distributionDiv.find('[fieldtype=family]').val();
    if (family === 'metalog') {
        distributionDiv.find('.metalog').css('display','block')
    }
    else {
       distributionDiv.find('.metalog').css('display','none')
    }

    if (family === 'generalized_beta') {
       distributionDiv.find('.generalized_beta').css('display','block')
    }
    else {
       distributionDiv.find('.generalized_beta').css('display','none')
    }
}
for (let i = 0; i < nDistributionsInitial; i++) {
    displayDistributionSpecificOptions(i)
}



function copySamplesClipboard(button){
    var selectContents = function(el) {
      var range = document.createRange();
      range.selectNodeContents(el);
      var sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
    };

    distributionDiv = $(button).closest('[distributionindex]')

    var textField = distributionDiv.find('.samples').get(0)

    /* Select the text field */
    selectContents(textField)

    /* Copy the text inside the text field */
    document.execCommand("copy");

    distributionDiv.find('.copySamplesResult').text('Done!')
}

function removePair(pairIndex,distributionIndex){
    distributionDiv = $("#distribution"+distributionIndex)

    isEmptyPair = distributionDiv.find('.pair'+pairIndex+' [fieldtype=P]').val() === '' && distributionDiv.find('.pair'+pairIndex+' [fieldtype=Q]').val() === '';

    npairs = parseInt(distributionDiv.find('[fieldtype=nb_pairs_to_display_hidden_field]').val())

    for (let j = pairIndex; j < npairs+1; j++) {

        distributionDiv.find('.pair'+(j)+' [fieldtype=P]').val( distributionDiv.find('.pair'+(j+1)+' [fieldtype=P]').val())
        distributionDiv.find('.pair'+(j)+' [fieldtype=Q]').val( distributionDiv.find('.pair'+(j+1)+' [fieldtype=Q]').val())
    }

    distributionDiv.find('.pair'+npairs+' [fieldtype=P]').val('')
    distributionDiv.find('.pair'+npairs+' [fieldtype=Q]').val('')

    distributionDiv.find('[fieldtype=nb_pairs_to_display_hidden_field]').val(npairs-1)

    displayNbPairs(distributionIndex)

    if (!isEmptyPair) {
        submitForm()
    }
}

function addPair(distributionIndex){
    distributionDiv = $("#distribution"+distributionIndex)
    distributionDiv.find('[fieldtype=nb_pairs_to_display_hidden_field]').val(
        parseInt(distributionDiv.find('[fieldtype=nb_pairs_to_display_hidden_field]').val())+1)

    displayNbPairs(distributionIndex)
    displayAddPairsButton(distributionIndex)
}

function displayAddPairsButton(distributionIndex) {
    distributionDiv = $("#distribution"+distributionIndex)

    if (distributionDiv.find('[fieldtype=nb_pairs_to_display_hidden_field]').val()<10){
        distributionDiv.find('.add_pair_button').css('visibility','visible')
    }
    else {
        distributionDiv.find('.add_pair_button').css('visibility','hidden')
    }
}
for (let i = 0; i < nDistributionsInitial; i++) {
    displayAddPairsButton(i)
}

function addDistr(){
    n = parseInt($('#n_distributions_to_display').val())+1
    $('#n_distributions_to_display').val(n)

    displayNbDistributions(n)
    displayAddDistrButton()
    displayMixtureComponentOptions()

    new_index = n-1
    displayNbPairs(new_index)
    displayConditionalFieldsByClass('metalog_boundedness','metalog_bounds',new_index)
    displayConditionalFieldsByFieldType('plot_custom_domain_bool','plot_custom_domain_FromTo',new_index)
    displayDistributionSpecificOptions(new_index)
    // submitForm()
}

function displayAddDistrButton() {
    if (parseInt($('#n_distributions_to_display').val())<3){
        $('.addDistrButton').css('visibility','visible')
    }
    else {
        $('.addDistrButton').css('visibility','hidden')
    }
}

function displayMixtureComponentOptions(){
    if (parseInt($('#n_distributions_to_display').val())===1){
        $('.mixtureComponentOptions').css('display','none')
    }
    else {
        $('.mixtureComponentOptions').css('display','flex')
    }
}

function removeDistr(distributionIndex){
    new_n = parseInt($('#n_distributions_to_display').val())-1
    $('#n_distributions_to_display').val(new_n)

     for (let j = distributionIndex+1; j < nDistributionsMax; j++) {
          formValues = $('#distribution'+j+' [fieldtype]').map(
                function(){
                    if ($(this).attr('type') === 'checkbox'){return $(this).prop('checked')}

                    else {return $(this).val()}
                }).get()

          $('#distribution'+(j-1)+' [fieldtype]').map(
              function (index,element){
                  if ($(this).attr('type') === 'checkbox'){$(this).prop('checked', formValues[index])}

                  else {$(this).val(formValues[index])}
              }
          )
    }
    displayNbDistributions(new_n)
    submitForm()
}

function highlightErrors(){
    for (let i = 0; i < nDistributionsInitial; i++) {
        if ($('#distribution'+i+' .errors').get().length>0){
            $('#distribution'+i).css('border-color','red')
        }
    }
}
highlightErrors()