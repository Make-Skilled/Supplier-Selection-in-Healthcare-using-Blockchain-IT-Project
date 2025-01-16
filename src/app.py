from web3 import Web3,HTTPProvider
from flask import Flask,render_template,redirect,request,session,url_for
import json
from werkzeug.utils import secure_filename
import os
import hashlib

app=Flask(__name__)
app.secret_key="M@keskilled0"

userManagementArtifactPath="../build/contracts/userManagement.json"
ProductManagementArtifactPath="../build/contracts/ProductManagement.json"
blockchainServer="http://127.0.0.1:7545"

def connectWithContract(wallet,artifact=userManagementArtifactPath):
    web3=Web3(HTTPProvider(blockchainServer)) # it is connecting with server
    print('Connected with Blockchain Server')

    if (wallet==0):
        web3.eth.defaultAccount=web3.eth.accounts[0]
    else:
        web3.eth.defaultAccount=wallet
    print('Wallet Selected')

    with open(artifact) as f:
        artifact_json=json.load(f)
        contract_abi=artifact_json['abi']
        contract_address=artifact_json['networks']['5777']['address']
    
    contract=web3.eth.contract(abi=contract_abi,address=contract_address)
    print('Contract Selected')
    return contract,web3

app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure base upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route('/')
def homePage():
    return render_template('index.html')

@app.route('/login')
def loginPage():
    return render_template('login.html')

@app.route('/signup')
def signupPage():
    return render_template('signup.html')

@app.route('/contact')
def contactPage():
    return render_template('contact.html')

@app.route('/services')
def servicesPage():
    return render_template('services.html')

@app.route('/about')
def aboutPage():
    return render_template('about.html')

@app.route('/manufacturerDashboard')
def manufacturerDashboard():
    contract,web3=connectWithContract(0)
    role ='supplier'
    response=contract.functions.viewUsersByRole(role).call()
    print(response)
    user_roles=[]
    for i in response:
        user_roles.append({
        "address": i[0],  # Ethereum address
        "username": i[1]
        })
    print(user_roles)
    return render_template('manufacturer.html',user_roles=user_roles)

@app.route('/supplierDashboard')
def supplierDashboard():
    message = request.args.get('message','')
    wallet=session['userwallet']
    contract1,web3=connectWithContract(0)
    role ='hospital'
    response=contract1.functions.viewUsersByRole(role).call()
    roles=[]
    for i in response:
        roles.append({
        "address": i[0],  # Ethereum address
        "username": i[1]
        })
    contract,web3=connectWithContract(wallet,ProductManagementArtifactPath)
    response1=contract.functions.getProductsBySupplier(wallet).call()
    print(response1)
    products=[]
    for i in response1:
        products.append(i)
    print(products)
    return render_template('supplier.html',roles=roles,product=products,message=message)

@app.route('/hospitalDashboard')
def hospitalDashboard():
    response=''
    return render_template('hospital.html',response=response)

@app.route('/register',methods=['POST']) # page (1 Route), page (2 Route)
def register():
    role=request.form['role']
    wallet=request.form['address']
    username=request.form['username']
    email=request.form['email']
    password=request.form['password']
    confirmPassword=request.form['confirmPassword']
    
    if(password!=confirmPassword):
        return render_template('signup.html',message='passwords not matched, try again')
    
    contract,web3=connectWithContract(wallet) # UserManagement
    try:
        tx_hash=contract.functions.userSignUp(wallet,username,password,role,email).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        print('Transaction Successful')
        return render_template('signup.html',message='Signup Successful')
    except:
        return render_template('signup.html',message='there is problem in creating account')

@app.route('/loginForm',methods=['POST'])
def loginForm():
    username=request.form['username']
    password=request.form['password']

    contract,web3=connectWithContract(0)
    try:
        result=contract.functions.userLogin(username,password).call()
        print(result)
        if result==True:
            response=contract.functions.viewUserByUsername(username).call()
            print (response)
            session['userwallet']=response[0]
            session['username']=response[1]
            session['userrole']=response[3]
            session['useremail']=response[-2]
            if session['userrole']=='manufacturer':
                return redirect('/manufacturerDashboard')
            elif session['userrole']=='supplier':
                return redirect('/supplierDashboard')
            elif session['userrole']=='hospital':
                return redirect('/hospitalDashboard')
            return render_template('login.html',message='success')
        else:
            return render_template('login.html',message='Invalid credentials')
    except Exception as e:
        return render_template('login.html',message='Invalid details of username')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/mproduct', methods=['post'])
def mProduct():
    wallet=session['userwallet']
    MName=request.form['manufacturer-name']
    supplier=request.form['supplier_add']
    MProductName=request.form['product-name']
    MPRoductID=request.form['product-id']
    MDate=str(request.form['expiry-date'])
    productImage=request.files['product-image']


    if productImage.filename == '' :
        return render_template('Lifeinsurance.html', message="No file selected for one or more fields.")

    # Create subdirectory path dynamically
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], session['userrole'])
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)  # Create folder if it doesn't exist

    # Secure and save files
    productImage_filename = secure_filename(productImage.filename)

    productImagePath = os.path.join(user_folder, productImage_filename)

    # Save files locally or to the specified directory
    productImage.save(productImagePath)

    # Generate hashes for the files
    productImage.seek(0)  # Reset the file pointer
    productImageHash = hashlib.sha256(productImage.read()).hexdigest()

    contract,web3=connectWithContract(0,ProductManagementArtifactPath)

    try:
        tx_hash=contract.functions.addProductWithSupplier(wallet,supplier,MName,MPRoductID,MProductName,MDate,productImagePath,productImageHash).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        print('Transaction Successful')
        return render_template('manufacturer.html',message='Product added Successfully')
    except Exception as e:
        print(e)
        return render_template('manufacturer.html',message='there is problem in adding Product')
    
@app.route('/supplier',methods=['post'])
def Supplier():
    wallet=session['userwallet']
    hospital=request.form['hospital_add']
    productID=request.form['product']

    contract,web3=connectWithContract(0,ProductManagementArtifactPath)

    try:
        tx_hash=contract.functions.linkSupplierWithHospital(wallet,hospital,productID).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        print('Transaction Successful')
        return redirect(url_for('supplierDashboard',message='Hospital added Successfully'))
    except Exception as e:
        print(e)
        return redirect(url_for('supplierDashboard',message='there is problem in adding Hospital'))
    
@app.route('/hospital', methods=['POST'])
def Hospital():
    productId = request.form['productid']
    contract, web3 = connectWithContract(0, ProductManagementArtifactPath)
    try:
        response = contract.functions.getProductDetails(productId).call()
        print(response)

        # Check if the response contains valid data
        if not response:
            return render_template('hospital.html', message="No product found with this ID.")

        # Create a dictionary to pass to the template
        product_details = {
            "manufacturer": response[0],
            "supplier": response[1],
            "hospital": response[2],
            "product_id": response[3],
            "product_name": response[4],
            "expiry_date": response[5],
            "image_url": response[6],  # Path to image
            "image_hash": response[7]
        }

        return render_template('hospital.html', product=product_details)
    except Exception as e:
        # Extract the error message
        message = "Product does not exist" if "Product does not exist" in str(e) else "An error occurred"
        print(message)
        return render_template('hospital.html', message=message)

    
if __name__=="__main__":
    app.run(host='0.0.0.0',port=4001,debug=True)