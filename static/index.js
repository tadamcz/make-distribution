function displayMetalogExample(){
    document.getElementById("nb_pairs_to_display_hidden_field").value = 3
    document.getElementById("family").value = 'metalog'

    document.getElementById("plot_custom_domain_bool").checked = true
    display_conditional_fields('plot_custom_domain_bool','plot_custom_domain_FromTo')

    document.getElementById("plot_custom_domain_FromTo-From").value = -100
    document.getElementById("plot_custom_domain_FromTo-To").value = 100


    document.getElementById("metalog_boundedness").checked = false
    display_conditional_fields('metalog_boundedness','metalog_bounds')

    document.getElementById("metalog_allow_numerical").checked = true

    document.getElementById("pairs-0-P").value = 0.1
    document.getElementById("pairs-0-Q").value = -20

    document.getElementById("pairs-1-P").value = .5
    document.getElementById("pairs-1-Q").value = -1

    document.getElementById("pairs-2-P").value = .9
    document.getElementById("pairs-2-Q").value = 50

    submitForm()

}

function displayBetaExample(){
    document.getElementById("nb_pairs_to_display_hidden_field").value = 3
    document.getElementById("family").value = 'beta'

    document.getElementById("plot_custom_domain_bool").checked = false
    display_conditional_fields('plot_custom_domain_bool','plot_custom_domain_FromTo')

    document.getElementById("pairs-0-P").value = .15
    document.getElementById("pairs-0-Q").value = .06

    document.getElementById("pairs-1-P").value = .5
    document.getElementById("pairs-1-Q").value = .21

    document.getElementById("pairs-2-P").value = .85
    document.getElementById("pairs-2-Q").value = .93

    submitForm()

}
function submitForm(){
    document.getElementById("dataInputForm").submit()
}
function display_nb_pairs() {
    const nb_pairs = document.getElementById("nb_pairs_to_display_hidden_field").value;
    const max_pairs = 10;
    let i;
    for (i = 1; i <= max_pairs; i++) {
        if (i <= nb_pairs) {
            document.getElementById("pair" + i).style.display = "block"
        } else {
            document.getElementById("pair" + i).style.display = "none"
        }
    }
    displayAddPairsButton()
    // displayRemovePairButtons()
}
display_nb_pairs()

function display_conditional_fields(checkboxdiv,fielddiv) {
    const checked = document.getElementById(checkboxdiv).checked
    if (checked) {
        document.getElementById(fielddiv).style.display = 'block'
    }
    else {
        document.getElementById(fielddiv).style.display = 'none'
    }
}

const conditionalFields = [
    {'checkbox':'metalog_boundedness','field':'metalog_bounds'},
    {'checkbox':'plot_custom_domain_bool','field':'plot_custom_domain_FromTo'}
]
for (const conditionalField of conditionalFields) {
    display_conditional_fields(conditionalField.checkbox,conditionalField.field)
}

function display_metalog_options() {
    const family = document.getElementById("family").value;
    if (family == 'metalog') {
        document.getElementById('metalog_options').style.display = 'block'
        const nb_pairs = document.getElementById("nb_pairs_to_display_hidden_field").value
        // if (nb_pairs_to_display_hidden_field < 3) {
        //     document.getElementById('nb_pairs_to_display_hidden_field').value = 3
        //     display_nb_pairs()
        // }

    }
    else {
        document.getElementById('metalog_options').style.display = 'none'
    }
}
display_metalog_options()

function copySamplesClipboard(){
    var selectContents = function(el) {
      var range = document.createRange();
      range.selectNodeContents(el);
      var sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
    };

    var textField = document.querySelector('#samples');

    /* Select the text field */
    selectContents(textField)

    /* Copy the text inside the text field */
    document.execCommand("copy");

    document.getElementById('copySamplesResult').innerText = 'Done!'
}

function removePair(i){
    isEmptyPair = document.getElementById("pairs-" + i + "-P").value === '' && document.getElementById("pairs-" + i + "-Q").value === '';

    npairs = document.getElementById("nb_pairs_to_display_hidden_field").value

    for (let j = i+1; j < npairs; j++) {
        document.getElementById("pairs-"+(j-1)+"-P").value = document.getElementById("pairs-"+j+"-P").value
        document.getElementById("pairs-"+(j-1)+"-Q").value = document.getElementById("pairs-"+j+"-Q").value
    }

    document.getElementById("pairs-"+(npairs-1)+"-P").value = ''
    document.getElementById("pairs-"+(npairs-1)+"-Q").value = ''

    document.getElementById("nb_pairs_to_display_hidden_field").value = document.getElementById("nb_pairs_to_display_hidden_field").value-1
    display_nb_pairs()

    if (!isEmptyPair) {
        submitForm()
    }
}

function addPair(){
    document.getElementById('nb_pairs_to_display_hidden_field').value = parseInt(document.getElementById('nb_pairs_to_display_hidden_field').value) + 1
    display_nb_pairs()
    displayAddPairsButton()
}

function displayAddPairsButton() {
    if (parseInt(document.getElementById('nb_pairs_to_display_hidden_field').value)<10){
        document.getElementById('add_pair_button').style.visibility = 'visible'
    }
    else {
        document.getElementById('add_pair_button').style.visibility = 'hidden'
    }
}
displayAddPairsButton()


