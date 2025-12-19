document.addEventListener('DOMContentLoaded', function() {

    // Use buttons to toggle between views
    document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
    document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
    document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
    document.querySelector('#compose').addEventListener('click', compose_email);

    // By default, load the inbox
    load_mailbox('inbox');
});

function compose_email() {

    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#single-email-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';
    document.querySelector('#alerts-view').style.display = 'none';

    // Clear out composition fields
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';

    // Send email when form is submitted
    document.querySelector('#compose-form').onsubmit = send_email;
}

function send_email() {
    recipients = document.querySelector('#compose-recipients').value.trim();
    subject = document.querySelector('#compose-subject').value.trim();
    body = document.querySelector('#compose-body').value.trim();

    fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body,
    })
    })
    .then(response => response.json())
    .then(result => {
        // Print result
        console.log(result);

        // If there is an error, take user back to compose view
        if (result.error) {
            compose_email;
            display_alert('danger', result.error);
        // Else take user to the sent pages
        } else {
            load_mailbox('sent');
        }
    })
    .catch(error => {
        console.log('Error: ', error);
    });
    // Prevent form from submitting
    return false;
}

function display_alert(type, message) {
    alert = document.querySelector('#alerts-view');
    alert.style.display = 'block';
    alert.innerHTML = `
    <div class="alert alert-${type}" role="alert">
        ${message}
    </div>`;
}

function load_mailbox(mailbox) {

    // Show the mailbox and hide other views
    document.querySelector('#emails-view').style.display = 'block';
    document.querySelector('#single-email-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#alerts-view').style.display = 'none';

    // Show the mailbox name
    document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

    // Get emails from that mailbox
    fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
        // Print emails
        console.log(emails);
        
        // Add div to display emails
        if (!document.querySelector("#myemails")) {
                const table = document.createElement('div');
                table.id = 'myemails';
                table.classList.add('container');

            document.querySelector('#emails-view').append(table);
        }
        
        let myemails = document.querySelector('#myemails');
        myemails.innerHTML = '';

        emails.forEach(email => {
            // Log which email we are at
            console.log(`Email: ${email.subject}`);
            
            // Status of email
            let status = 'unread';
            if (email.read) {
                status = 'read';
            }
            
            // Add row which displays information about the emails
            let row = document.createElement('div');
            row.classList.add('row', 'border', 'border-dark', `${status}`);
            
            row.innerHTML = `
            <div class="col-3">
                <b>${email.sender}</b>
            </div>
            <div class="col-6">
                ${email.subject}
            </div>
            <div class="col-3 email-timestamp">
                ${email.timestamp}
            </div>`;

            myemails.append(row);

            // Display email when the row is clicked
            row.onclick = () => {
                // Disable archive for emails in the sent mailbox 
                archiveEnabled = true;
                if (mailbox === 'sent') {
                    archiveEnabled = false;
                }                   
                display_email(email.id, archiveEnabled);
            };
        });
    });
}

function display_email(emailId, archiveEnabled) {

    // Show single email view and hide the other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#single-email-view').style.display = 'block';
    document.querySelector('#compose-view').style.display = 'none';
    
    // Log email we are currently displaying
    console.log('Displaying Email ' + emailId);
    
    // Get information about the email
    fetch(`/emails/${emailId}`)
    .then(response => response.json())
    .then(email => {
        // Print email
        console.log(email);

        singleEmailView = document.querySelector('#single-email-view');
        singleEmailView.innerHTML = ''

        // Display information about the email
        const info = document.createElement('div');
        info.innerHTML = `
        <p class="mb-0"><b>From: </b>${email.sender}</p>
        <p class="mb-0"><b>To: </b>${email.recipients}</p>
        <p class="mb-0"><b>Subject: </b>${email.subject}</p>
        <p class="mb-0"><b>Timestamp: </b>${email.timestamp}</p>
        `;

        // Reply button
        const replyButton = document.createElement('button');
        replyButton.type = 'button';
        replyButton.innerHTML = 'Reply';
        replyButton.classList.add('btn', 'btn-outline-primary');
        replyButton.addEventListener('click', () => {
            reply_email(email);
        });

        // Archive/Unarchive button
        const archiveButton = document.createElement('button');
        archiveButton.type = 'button';

        // Set display for archive button to none if email is from sent mailbox
        if (!archiveEnabled) {
            archiveButton.style.display = 'none';
        // Else add class, innerHTML and event listener to the button
        } else {
            archiveButton.classList.add('btn', 'btn-outline-secondary', 'ml-1');
            if (!email.archived) {
                archiveButton.innerHTML = 'Archive';
            } else {
                archiveButton.innerHTML = 'Unarchive';
            }
            archiveButton.addEventListener('click', () => {
                archive_email(email.id, email.archived);
            });
        }
        
        // Seperate the top section from the botton
        const hr = document.createElement('hr');

        // Display body of email
        const body = document.createElement('div');
        body.innerHTML = `
        <p>${email.body.replaceAll('\n', '<br>')}</p>`;

        // Append all elements to the view
        [info, replyButton, archiveButton, hr, body].forEach(element => {
            if (element !== null) {
                singleEmailView.append(element);
            }
        })

        // Mark email as read if it is not yet read
        if (!email.read) {
            fetch(`/emails/${email.id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    read: true
                })
            });
        }
    });
}

function reply_email(email) {
    // Load compose view
    compose_email();
    
    // Fill in recipient field with the sender
    document.querySelector('#compose-recipients').value = email.sender;

    // Fill in subject adding 'Re: ' if the subject did not start with it originally
    let subject = email.subject;
    if (!subject.startsWith('Re:')) {
        subject = 'Re: ' + subject;
    }
    document.querySelector('#compose-subject').value = subject;
    
    // Fill in body with the template reply format
    document.querySelector('#compose-body').value = `\nOn ${email.timestamp} ${email.sender} wrote:\n${email.body}`;
}

function archive_email(emailId, emailArchived) {
    // Reverse email's archived status, eg. if the email is archived, set it to unarchived
    fetch(`/emails/${emailId}`, {
        method: 'PUT',
        body: JSON.stringify({
            archived: !emailArchived
        })
    })
    .then(response => {
        // Log response
        console.log(response);
        
        // Load inbox
        load_mailbox('inbox');
    });
}