$( document ).ready(function() {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    $('#addtocart').on('click', function (){
        let item = $('#item_id').val();
        let count = $('#count').val();
        $.ajax({
            method: 'GET',
            url: '/addtocart/',
            data: {'item':item, 'count':count},
            success: function (){
                window.location.replace("/cart");
            }
        });
    });

    $('#buy').on('click', function (){
        let item = $('#item_id').val();
        let count = $('#count').val();
        $.ajax({
            method: 'POST',
            url: '/buy/'+item,
            data: {
                'count':count,
                'csrfmiddlewaretoken': getCookie('csrftoken')
            },
            success: function (session){
                let stripe = Stripe(session['public_key']);
                stripe.redirectToCheckout({ sessionId: session['session'] })
            }
        });
    });

    $('#buycart').on('click', function (){
        let promocode = ''
        if ($('#promocode').prop('disabled')===true){
            promocode = $('#promocode').val()
        }
        let order = [];
        $('.card-body').each(function (){
           order.push([$(this).find('.item_id').val(), $(this).find('.count').text()]);
        });
        $.ajax({
            method: 'POST',
            url: '/buyorder/',
            data: {
                'order[]':order,
                'promocode': promocode,
                'csrfmiddlewaretoken': getCookie('csrftoken')
            },
            success: function (session){
                console.log(session.status)
                let stripe = Stripe(session['public_key']);
                stripe.redirectToCheckout({ sessionId: session['session'] })
            },
            error: function(info){
                alert(info['responseText']);
            },
        });
    });

    $('#checkcode').on('click', function (){
       let code = $('#promocode').val()
       $.ajax({
            method: 'POST',
            url: '/checkpromo/',
            data: {
                'code': code,
                'csrfmiddlewaretoken': getCookie('csrftoken')
            },
            success: function (info){
                if (info!=='bad'){
                    $('#checkcode').prop('disabled', true)
                    $('#promocode').prop('disabled', true)
                    $('#promocode').css('background-color', 'lightgreen')
                    let newpricepercent = ((100-parseInt(info))/100)
                    $('#fullamount').text(parseInt($('#fullamount').text())*newpricepercent)
                }
                else{
                    $('#promocode').css('background-color', 'lightcoral')
                }
            }
        });
    });
    document
      .querySelector("#payment-form")
      .addEventListener("submit", handleSubmit);
    let stripe = ''
    let elements = ''
    if ((window.location.pathname === '/cart') && ($('.emptycart').length===0)){
        let order = [];
        $('.card-body').each(function (){
           order.push([$(this).find('.item_id').val(), $(this).find('.count').text()]);
        });
        $.ajax({
            method: 'POST',
            url: '/checkcart/',
            data: {
                    'order[]':order,
                    'csrfmiddlewaretoken': getCookie('csrftoken')
            },
            success: function (info){
                $('#payinfo').attr('hidden', false)
                $('#cartamount').append(' '+info)
            },
            error: function (info){
                alert(info['responseText'])
            }
        });
        $('#paymentintent').on('click', function (){
            let promocode = ''
            if ($('#promocode').prop('disabled')===true){
                promocode = $('#promocode').val()
            }
            $.ajax({
                method: 'POST',
                url: '/create-payment-intent/',
                data: {
                    'order[]':order,
                    'promocode': promocode,
                    'csrfmiddlewaretoken': getCookie('csrftoken')
                },
                success: function (info){
                    stripe = Stripe(info['public_key']);
                    const clientSecret = info['clientSecret'];
                    const appearance = {
                        theme: 'stripe',
                    };
                    elements = stripe.elements({ appearance, clientSecret});
                    const paymentElementOptions = {
                        layout: "tabs",
                    };
                    $('#paymentintent').attr('hidden', true)
                    $('#payment-form').attr('hidden', false)
                    const paymentElement = elements.create("payment", paymentElementOptions);
                    paymentElement.mount("#payment-element");
                    checkStatus()
                },
                error: function (info){
                    alert(info['responseText'])
                }
            });
        })
    }

    async function handleSubmit(e) {
      e.preventDefault();
      setLoading(true);

      const { error } = await stripe.confirmPayment({
        elements,
        confirmParams: {
          // Make sure to change this to your payment completion page
          return_url: window.location.href,
        },
      });

      // This point will only be reached if there is an immediate error when
      // confirming the payment. Otherwise, your customer will be redirected to
      // your `return_url`. For some payment methods like iDEAL, your customer will
      // be redirected to an intermediate site first to authorize the payment, then
      // redirected to the `return_url`.
      if (error.type === "card_error" || error.type === "validation_error") {
        showMessage(error.message);
      } else {
        showMessage("An unexpected error occurred.");
      }

      setLoading(false);
    }

    // Fetches the payment intent status after payment submission
    async function checkStatus() {
      const clientSecret = new URLSearchParams(window.location.search).get(
        "payment_intent_client_secret"
      );

      if (!clientSecret) {
        return;
      }

      const { paymentIntent } = await stripe.retrievePaymentIntent(clientSecret);

      switch (paymentIntent.status) {
        case "succeeded":
          showMessage("Payment succeeded!");
          break;
        case "processing":
          showMessage("Your payment is processing.");
          break;
        case "requires_payment_method":
          showMessage("Your payment was not successful, please try again.");
          break;
        default:
          showMessage("Something went wrong.");
          break;
      }
    }

    // ------- UI helpers -------

    function showMessage(messageText) {
      const messageContainer = document.querySelector("#payment-message");

      messageContainer.classList.remove("hidden");
      messageContainer.textContent = messageText;

      setTimeout(function () {
        messageContainer.classList.add("hidden");
        messageText.textContent = "";
      }, 4000);
    }

    // Show a spinner on payment submission
    function setLoading(isLoading) {
      if (isLoading) {
        // Disable the button and show a spinner
        document.querySelector("#submit").disabled = true;
        document.querySelector("#spinner").classList.remove("hidden");
        document.querySelector("#button-text").classList.add("hidden");
      } else {
        document.querySelector("#submit").disabled = false;
        document.querySelector("#spinner").classList.add("hidden");
        document.querySelector("#button-text").classList.remove("hidden");
      }
    }

});