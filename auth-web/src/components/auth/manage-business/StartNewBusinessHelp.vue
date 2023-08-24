<template>
  <section>
    <h3 class="text-center">
      Help with Starting and Managing a Business
    </h3>
    <div class="mt-10">
      <p class="ml-1">
        Start a named or numbered business in B.C. by following these steps:
      </p>
      <ol class="bold">
        <li class="mt-8">
          <h4>Decide on a Business Type</h4>
          <ul class="mt-4 text-align ml-n6">
            <li>
              Decide which business structure is the most appropriate for you. A few options are: a sole
              proprietorship, partnership, or corporation. Each structure has different legal and financial
              implications. <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
              <a href="https://entity-selection-prod.apps.silver.devops.gov.bc.ca/">
                Use the Business Structures Wizard to help you decide.</a>
            </li>
            <li>
              If you want to start a corporation, you also have the choice of using a named or numbered company.
            </li>
            <li>
              Once your Name Request has been approved you must return to this screen to Incorporate or Register your
              business using your approved Name Request.
            </li>
          </ul>
        </li>

        <li class="mt-10">
          <h4>Request a Business Name or Use a Numbered Company</h4>
          <ul class="mt-4 ml-2 ml-n6 text-align">
            <h4 class="mb-5">
              Request a Business Name
            </h4>
            <li>
              To start a named business in B.C., change the business name of an existing company, or
              merge two or more companies using a new name, click the
              <strong>"Get Started with a B.C. Based Business"</strong> button on this
              screen and follow the instructions.
            </li>
            <li>
              Before registering or incorporating a named business, you will need to first submit a Name Request.
              You will be asked to create a unique name for your business and submit your name(s) for review by BC
              Registries staff.
            </li>
            <li>
              Once you submit your Name Request you can return to this screen and your Name Request (NR) will
              automatically appear in your table.
            </li>
            <li>
              If you do not see your Name Request in your table (e.g. if you submitted your Name Request without
              being logged into your BC Registries account), you can add your Name Request manually by looking up
              your business name or your NR &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;number.
            </li>
            <li>
              You can track the approval status of your Name Request from your table on this screen by clicking the
              <strong>"Open Name Request"</strong> button next to your Name Request.
            </li>
            <h4 class="my-5">
              Use a Numbered Company
            </h4>
            <li>
              To start a numbered corporation in B.C., click the <strong>"Get Started with a B.C. Based
                Business"</strong> button and follow the instructions.
            </li>
          </ul>
        </li>
        <li class="mt-10">
          <h4>Incorporate or Register Your Business</h4>
          <ul class="mt-4 ml-2 ml-n6 text-align">
            <li>
              For named businesses, once your Name Request has been approved and added to your table on
              this screen, you must select the <strong>"Register Now"</strong> button beside the name to begin
              your incorporation or registration.
            </li>
            <li>
              Follow the steps in the application and complete all of the required information including addresses,
              contact information, people and roles, and share structure (if applicable).
            </li>
            <li>
              Retain a copy of all incorporation or registration documents for your business' records.
            </li>
          </ul>
        </li>

        <li class="mt-10">
          <h4>Manage and Maintain Your Business</h4>
          <ul class="mt-4 ml-2 ml-n6 text-align">
            <li>
              Once your business is incorporated or registered you are required to keep information about your
              business up to date with the Business Registry.
            </li>
            <li>
              From your table, click <strong>"Manage Business"</strong> to manage and maintain your
              business information including:
            </li>
            <ul>
              <li>
                View and change business information.
              </li>
              <li>
                See when annual reports are due and file them each year (if applicable).
              </li>
              <li>
                See the history of your business' filings and download copies of all documents.
              </li>
              <li>
                Dissolve your business.
              </li>
            </ul>
          </ul>
        </li>
      </ol>
    </div>
  </section>
</template>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
ol.bold li::marker {
  font-weight: bold;
  font-size: $px-16 !important;
  color: $gray9;
  margin:5px 20px 5px 0px;
}

ul {
  list-style-type: none;
}

ul li {
  margin-bottom: 10px;
}

ul li::before {
  content: "•";
  font-style:bold;
  line-height: 1em;
  margin:5px 20px 10px 0px;
}

li ul li:before {
  float: left;
}

li ul ul li:before {
  float: none;
  margin-bottom: 50px;
}

ul ul li {
  margin-bottom: 5px;
}

</style>
