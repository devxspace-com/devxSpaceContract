// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Script.sol";
import "../src/DevXspace.sol";

contract DevXspaceScript is Script {
    DevXspace devxspace;
    function setUp() public {}

    function run() public {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);
        devxspace = new DevXspace(0x9B69F998b2a2b20FF54a575Bd5fB90A5D71656C1, 0x75c5C6E08C2Cd06C7fB6a484a1d7C8d6901d4B65, 0);
        vm.broadcast();
    }
}
