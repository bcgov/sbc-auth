<template>
  <div id="dashboard-help">
    <div class="mt-n2 mb-8">
      <v-btn
        text
        color="primary"
        id="btn-buissness-help"
        class="mt-n6 px-0"
        @click="helpTextView = !helpTextView"
      >
        <v-icon>mdi-help-circle-outline</v-icon>
        <span>
          {{ helpTextView ? 'Close Help' : 'Help with Starting a Business' }}
        </span>
      </v-btn>
    </div>

    <div v-if="helpTextView" id="business-help-text" class="my-8 pt-8 pb-2">
      <header id="help-dropdown-header" align="center" class="mb-6">
        <strong>Help with Starting a Business</strong>
      </header>
      <body id="help-text-body" class="mx-12 px-12">
        <p class="my-6">Start a named or numbered business in
          B.C. by following these steps:
        </p>
        <ol>
          <li class="py-2"><strong>Decide on a Business Type</strong></li>
            <ul>
              <li class="py-2">Decide which business structure is most appropriate
                for you. A few options are: a sole proprietorship
                partnership, or corporation. Each structure has
                different legal and financial implications.
                <a class="help-text-link" @click="goToSelectorWizard">
                  Use the Business Structures Wizard to help you decide.
                </a>
                <v-icon small color="primary" class="mt-n1">mdi-open-in-new</v-icon>
              </li>
              <li class="py-2">If you want to start a corporation, you also have the
                choice of using a named or numbered company.
              </li>
            </ul>
          <li class="py-4">
            <strong>Request a Business Name or Use a Numbered Company</strong>
          </li>
            <ul>
              <li class="py-2">If you would like to start a named
                business, the first step is is to
                <a class="help-text-link" @click="goToNameRequest()">
                  submit a Name Request
                </a>.
                Select "Request a Business Name" and create a unique name
                for your business and submit this name for examination by
                the Business Registry.
              </li>
              <li class="py-2">You do not need to submit a Name Request
                if you are starting a numbered company.
              </li>
            </ul>
          <li class="py-2"><strong>Incorporate or Register</strong></li>
            <ul>
              <li class="py-2">If you requested your business name
                through your account, you will need to add your Name
                Request to your dashboard manually using your NR
                number. You can track the approval status of your Name
                Request by opening it from your Business Registry dashboard.
              </li>
              <li class="py-2">If one of your requested names is
                approved, you can use it to incorporate or register you
                business by selecting "Use this Name Request Now" from
                the dropdown menu for you Name Request.
              </li>
              <li class="py-2">For a numbered company, select "Start a
                Numbered Company", and select the type of numbered
                company you would like to start.
              </li>
              <li class="py-2">Follow the steps in the incorporation
                application or registration and complete all of the
                required information including; addresses, contact
                information, people and roles, and share structure
                (when applicable).
              </li>
              <li class="py-2">Retain a copy of all incorporation or
                registration documents for your business' records.
              </li>
            </ul>
          <li class="py-2"><strong>Manage and Maintain Your Business</strong></li>
            <ul>
              <li class="py-2">Once your business is incorporated or
                registered you are required to keep information about
                your business up to date with the Business Registry.
                </li>
                <li class="py-2"> By managing your business through
                  your BC Registries you can:
                <ul>
                  <li class="py-2">View and change company information.</li>
                  <li class="py-2">See when annual reports are due and
                    file them each year (if applicable).
                  </li>
                  <li class="py-2">See the history of your business'
                    filings and download copies of all documents.
                  </li>
                  <li class="py-2">Dissolve your business (coming soon
                    to all business types).
                  </li>
                </ul>
              </li>
            </ul>
        </ol>
      </body>
      <footer align="right">
        <v-btn
          text
          class="px-0"
          color="primary"
          @click="helpTextView = !helpTextView"
        >
          <span><u>Hide Help</u></span>
        </v-btn>
      </footer>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import { appendAccountId } from 'sbc-common-components/src/util/common-util'

@Component({})
export default class DashboardHelp extends Vue {
  @Prop({ default: false }) helpTextView: boolean

  // open Business Structures Wizard
  goToSelectorWizard (): void {
    window.location.href = ConfigHelper.getEntitySelectorUrl()
  }

  // open Name Request
  goToNameRequest (): void {
    window.location.href = appendAccountId(ConfigHelper.getNameRequestUrl())
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

#business-help-text {
  border-bottom: dashed;
  border-top: dashed;
  border-bottom-width: 1px;
  border-top-width: 1px;
}

#help-dropdown-header {
  color: black;
}

li, p {
  color: $gray7;
}

ul {
  list-style-type: disc;
}

.help-text-link {
  text-decoration: underline;
}
</style>
