var forms = document.getElementsByClassName('submit-answer');
  for (let form of forms) {
      form.addEventListener('submit', function(evt) {
        evt.preventDefault();
        submit_answer(evt);
        evt.preventDefault();
      });
  }