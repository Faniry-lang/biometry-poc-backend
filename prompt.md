This is a minimal flask project for a poc (proof of concept) application.
For us to be able to do so, here's some task I need you to do:
  - Add a new column to the clients table in db.sql named fingerprint as BLOB nullable
  - Modify the Clients model in models.py by adding the new column to it
  - In app.py create an endpoint for adding fingerprint to a client
    - endpoint receives client id and fingerprint as string and updates the client
  - Create another endpoint for creating a client

#### Task 2
In Biometry_authentication_poc_back (flask app)
- add an endpoint to fetch clients by id BUT without the fingerprint column
  - endpoint is /get-client-by-id 
- create an endpoint to fetch clients fingerprint by client id
  - endpoint is /get-finger-print-by-clientid

In Biometry_authentication_poc (react-native)
  - Create a hook use-fingerreader.ts 
    - The hook should have the followings methods: scanFingerprint(timeout: number): string and compareFingerprints(f1: string, f2: string): boolean
      - The content of these methods is empty for now (to be implemented yet) 
      - scanFingerprint returns a random string 
      - compareFingerprints returns true for now
  - In the home page of the react native app, replace the content by three buttons: 
    - Opérations Client
    - Acquisition Client
  - Create a new component "IdentificationClientScreen" with a ID input.
    - A "Continuer" Button that will:
      - fetch from localhost:5000/get-client-by-id  
      - store the client id, firstname and lastname in async storage
      -  nagivate to a new component ClientOperation
  - Create ClientOperation
    - Content: one button "Solde" 
    - When hitting the button, a screen appears asking the user to scan their fingerprint with a button: Scan fingerprint using the use-fingerreader hook. 
      - first fetch clients (stored in async storage) fingerprint
      - then compare it with the new fingerprint scanned with scanFingerprint
      - if the method compareFingerprint returns false, display an error message saying client not authenticated, if true then display a screen saying "Un message a été envoyé au client" 

N.B: all of the screens must have a title and a "Retour" button somewhere