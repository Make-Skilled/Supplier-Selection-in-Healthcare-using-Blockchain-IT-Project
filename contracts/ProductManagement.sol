// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ProductManagement {
    struct Product {
        address manufacturer;
        address supplier;
        address hospital;
        string manufacturerName;
        string productId;
        string productName;
        string manufactureDate;
        string imagePath;
        string imageHash;
    }

    // Mappings to store the relationships
    mapping(string => Product) public products;
    mapping(address => string[]) public manufacturerProducts;
    mapping(address => string[]) public supplierProducts;
    mapping(address => address[]) public supplierHospitals;

    // Events to track changes
    event ProductAdded(address indexed manufacturer, address indexed supplier, string productId);
    event ProductTraceabilityUpdated(address indexed supplier, address indexed hospital, string productId);

    // Function 1: Manufacturer adds a product with a supplier
    function addProductWithSupplier(
        address manufacturer,
        address supplier,
        string memory manufacturerName,
        string memory productId,
        string memory productName,
        string memory manufactureDate,
        string memory imagePath,
        string memory imageHash
    ) public {
        require(bytes(products[productId].productId).length == 0, "Product ID already exists.");
        
        // Create and store the product
        products[productId] = Product({
            manufacturer: manufacturer,
            supplier: supplier,
            hospital: address(0), // Hospital is not assigned yet
            manufacturerName: manufacturerName,
            productId: productId,
            productName: productName,
            manufactureDate: manufactureDate,
            imagePath: imagePath,
            imageHash: imageHash
        });

        // Link the product to the manufacturer and supplier
        manufacturerProducts[manufacturer].push(productId);
        supplierProducts[supplier].push(productId);

        emit ProductAdded(manufacturer, supplier, productId);
    }

    // Function 2: Supplier adds the product to the hospital
    function linkSupplierWithHospital(
        address supplier,
        address hospital,
        string memory productId
    ) public {
        require(bytes(products[productId].productId).length != 0, "Product does not exist.");
        require(products[productId].supplier == supplier, "Supplier not linked to this product.");

        // Update the product with the hospital
        products[productId].hospital = hospital;

        // Link supplier to hospital for traceability
        supplierHospitals[supplier].push(hospital);

        emit ProductTraceabilityUpdated(supplier, hospital, productId);
    }

    // Get all products by manufacturer
    function getProductsByManufacturer(address manufacturer) public view returns (string[] memory) {
        return manufacturerProducts[manufacturer];
    }

    // Get all products by supplier
    function getProductsBySupplier(address supplier) public view returns (string[] memory) {
        return supplierProducts[supplier];
    }

    // Get all hospitals linked to a supplier
    function getHospitalsBySupplier(address supplier) public view returns (address[] memory) {
        return supplierHospitals[supplier];
    }

    // Get product details, including manufacturer, supplier, and hospital
    function getProductDetails(string memory productId) public view returns (
        address manufacturer,
        address supplier,
        address hospital,
        string memory productIdOut,
        string memory productName,
        string memory manufactureDate,
        string memory imagePath,
        string memory imageHash
    ) {
        Product memory product = products[productId];
        require(bytes(product.productId).length != 0, "Product does not exist.");
        return (
            product.manufacturer,
            product.supplier,
            product.hospital,
            product.productId,
            product.productName,
            product.manufactureDate,
            product.imagePath,
            product.imageHash
        );
    }
}
