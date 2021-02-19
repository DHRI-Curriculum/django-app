Object.prototype.allFalse = function() {
    for (var i in this) {
        if (this[i] === true) return false;
    }
    return true;
}

function disable_all_elements(elemList) {
  for (x in elemList) {
    target_elem = elemList[x]
    if (typeof target_elem == 'object') {
      target_elem.classList.add('disabled');
      target_elem.disabled = true;
    }
  }
}

function enable_all_elements(elemList) {
  for (x in elemList) {
    target_elem = elemList[x]
    if (typeof target_elem == 'object') {
      target_elem.classList.remove('disabled');
      target_elem.disabled = false;
    }
  }
}

function submit_answer(e) {
  answers = {};

  let questionID = e.target.dataset.qid;
  let alertDiv = document.querySelector(`#alert-${questionID}`);
  let elems = [...e.target.elements]

  elems = elems.filter(e=>{return typeof(e) === 'object' &&
  e.dataset &&
  e.dataset.answer_id});

  elems.forEach(e => {
    answers[e.dataset.answer_id] = e.checked;
  });

  if (answers.allFalse()) {
    alertDiv.innerText = "At least one response is true. Choose one!"
    alertDiv.classList.remove('d-none');
    return false;
  }

  // disable all buttons and get all the answers
  disable_all_elements(elems);

  fetch('/workshops/{{ workshop.slug }}/lessons/check-answer/', {
      method: "POST",
      credentials: "same-origin",
      headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Accept": "application/json",
          "Content-Type": "application/json",
          "Question": questionID,
          "Answers": JSON.stringify(answers)
      },
      body: ''
  }).then(function(response) { return response.json();
  }).then(function(data) {
      if (data.error == null) {
        if (data.all_correct == true) {
          alertDiv.classList.add('d-none');
          e.target.parentElement.style = 'background-color: rgba(0, 170, 100, 0.1) !important;';
          e.target.getElementsByTagName('button')[0].classList.remove('btn-primary');
          e.target.getElementsByTagName('button')[0].classList.add('btn-success');
          e.target.getElementsByTagName('button')[0].classList.add('disabled');
          e.target.getElementsByTagName('button')[0].innerHTML = 'Correct answer!';
          return true;
        } else {
          //console.log('set to try again!')
          e.target.parentElement.style = 'background-color: #3498db63 !important;';
          alertDiv.innerText = "Unfortunately, that was not the correct answer. Try again!";
          alertDiv.classList.remove('d-none');
          enable_all_elements(elems);
          return false;
        }
      } else {
        console.error(data.error);
      }
  }).catch(function(ex) {
      console.error(ex);
  });

}