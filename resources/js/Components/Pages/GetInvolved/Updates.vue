<!--
  This example requires some changes to your config:
  
  ```
  // tailwind.config.js
  module.exports = {
    // ...
    plugins: [
      // ...
      require('@tailwindcss/forms'),
    ],
  }
  ```
-->
<template>
    <div class="container info_page" id="subscribe">
        
        <h1>Subscribe</h1>
        <p>GET A WEEKLY UPDATE</p>
<p>At Clayton.TV we strive to bring Christ-centred, biblical videos into one place with fresh content weekly. Our aim is to support and equip Christians around the world. If you find our work helpful, and would like regular email updates from Clayton.TV, please opt-in here (you can opt out at any time)…</p>
        <form action="//clayton.us2.list-manage.com/subscribe/post" method="POST">
            
            <input type="hidden" name="u" value="d5c4aef36a582de40d5837112">
            <input type="hidden" name="id" value="8fc2472183">

            <fieldset>

                <label class="text_input">
                    <b class="field_label" style="display:none;">Email Address</b>
                    <input type="email" autocapitalize="off" autocorrect="off" name="MERGE0" id="MERGE0" size="25" value="" placeholder="Email Address">
                </label>

                <label class="text_input">
                    <b class="field_label" style="display:none;">First Name</b>
                    <input type="text" name="MERGE1" id="MERGE1" size="25" value="" placeholder="First Name">
                </label>

                <label class="text_input">
                    <b class="field_label" style="display:none;">Last Name</b>
                    <input type="text" name="MERGE2" id="MERGE2" size="25" value="" placeholder="Last Name">
                </label>

                <fieldset class="radio_input">

                        <input type="hidden" name="EMAILTYPE" id="EMAILTYPE_HTML" value="html" checked="">

                    <!--<b class="field_label">Preferred format</b>

                    <label for="EMAILTYPE_HTML">
                        <input type="radio" name="EMAILTYPE" id="EMAILTYPE_HTML" value="html" checked>
                        <span>
                        HTML
                    </span>
                    </label>

                    <label for="EMAILTYPE_TEXT">
                        <input type="radio" name="EMAILTYPE" id="EMAILTYPE_TEXT" value="text" >
                        <span>
                        Text
                    </span>
                    </label>-->

                </fieldset>

                <button type="submit">Subscribe</button>
            </fieldset>
        </form>

        <p style="font-size: 1.3em;">You can change your mind at any time by clicking the unsubscribe link in the footer of any email you receive from us, or by contacting us at <a href="mailto:enquiries@clayton.tv">enquiries@clayton.tv</a>. We will treat your information with respect. For more information about our <a href="/Clayton_TV_Data_Privacy_Notice.pdf" target="_blank">privacy practices please click here</a>.</p>

        <p style="font-size: 1.3em;">By clicking above, you agree that we may process your information in accordance with these terms.</p>

        <p style="font-size: 1.1em;">We use MailChimp as our marketing automation platform. By clicking above to submit this form you acknowledge that the information you provide will be transferred to MailChimp for processing in accordance with their <a href="https://mailchimp.com/legal/privacy/" target="_blank">Privacy Policy</a> and <a href="https://mailchimp.com/legal/terms/" target="_blank">Terms</a>.</p>

        <a class="back_to_top" href="#masthead">Back to the top</a>   

    </div>
  </template>
  
  <script setup>
  import { PhotoIcon, UserCircleIcon } from '@heroicons/vue/24/solid'

  </script>
