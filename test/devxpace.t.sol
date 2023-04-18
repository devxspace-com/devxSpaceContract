// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity ^0.8.17;

import "../lib/forge-std/src/Test.sol";
import "../src/DevXspace.sol";
import "../src/DXcoin.sol";
import "../src/escrow.sol";

contract DevXspaceTest is Test {
    DevXspace devxspace;
    TokenERC20 devxcoin;
    EscrowByAgentV2 escrow;
    address buyer = mkaddr("buyer");
    address seller = mkaddr("seller");
    address agent = mkaddr("agent");
    address owner = mkaddr("owner");


    function setUp() public {
        vm.startPrank(agent);
       devxcoin = new TokenERC20("DXcoin", "DXC");
       escrow = new EscrowByAgentV2(500, 500, 2);
       devxspace = new DevXspace(agent, 1, 25, 5, 0);
       devxcoin.mint(agent, 5 ether);  
        vm.stopPrank();
    }

    function testcreateBuyerProfile() public{
        vm.startPrank(buyer);
        devxspace.createBuyerProfile(buyer);
        vm.stopPrank();             
    }

  function testcreateSellerProfile() public {
    vm.startPrank(seller);
    string[2] memory skills = ["html", "css"];
    string[] memory dynamicSkills = new string[](skills.length);
    for (uint i = 0; i < skills.length; i++) {
        dynamicSkills[i] = skills[i];
    }
    devxspace.createSellerProfile(seller, dynamicSkills);
    vm.stopPrank();             
}

function testcreateGig() public{
    testcreateSellerProfile();
    vm.startPrank(seller);
    devxspace.createGig(1 ether, "create a weebsite", "https://blahblahblah.com");
    vm.stopPrank();
}

function testgetGig() public{
    testcreateGig();
    devxspace.getGig(seller, 0);
}

function testgetAllgigs() public{
    // testcreateGig();
    testcreateGig();
    devxspace.getAllgigs();
}

function testhire() public returns(uint id){
    testcreateBuyerProfile();
    testcreateSellerProfile();
    testcreateGig();
    vm.startPrank(buyer);
    id = devxspace.hire("test", "test hire",seller, 22, 1 ether);
    vm.stopPrank();
}

// function testgetTasksForBuyer() public{
//     testhire();
//     devxspace.getTasksForBuyer(buyer);

// }

// function testgetTasksForSeller() public{
//     testhire();
//     devxspace.getTasksForSeller(seller);

// }
function testAcceptTask() public {
    testhire();
    vm.startPrank(seller);
    devxspace.AcceptTask(1);
    vm.stopPrank();
    devxspace.getTasksForSeller(seller);
    devxspace.getTasksForBuyer(buyer);
    
}

function testpayWithEth() public {
    testAcceptTask();
    vm.startPrank(buyer);
    vm.deal(buyer, 100 ether);
    devxspace.payWithEth{value: 1 ether}(seller, 1);
    vm.stopPrank();
}

// function testpayWithToken() public {
//     testAcceptTask();
//     vm.startPrank(buyer);
//     vm.deal(buyer, 100 ether);
//     devxcoin.approve(address(devxspace), 1 ether);
//     address token = address(devxspace);
//     devxspace.payWithToken(IERC20(token), seller, 1);
//     vm.stopPrank();
// }
function testRejectTask() public{
    testhire();
    vm.startPrank(seller);
    devxspace.RejectTask(1);
    vm.stopPrank();
}

function testAbortTask() public {
    testhire();
    testpayWithEth();
    vm.startPrank(seller);
    devxspace.AbortTask(1);
    vm.stopPrank();
}

function testSubmitTask() public{
    testpayWithEth();
    vm.startPrank(seller);
    devxspace.SubmitTask(1);
    vm.stopPrank();
}
function testAcceptSubmission() public{
        testpayWithEth();
        vm.prank(seller);
        devxspace.SubmitTask(1);
        devxspace.getTasksForBuyer(buyer);
        vm.startPrank(buyer);
        devxspace.AcceptSubmission(1);
        vm.stopPrank();
}

function testRejectSubmission() public{
        testpayWithEth();
        vm.prank(seller);
        devxspace.SubmitTask(1);
        devxspace.getTasksForBuyer(buyer);
        vm.startPrank(buyer);
        devxspace.RejectSubmission(1);
        vm.stopPrank();
}







    // function testPaymentWithToken() public {
    //     testAcceptTask();
    //     vm.startPrank(buyer);
    //     devxcoin.approve(address(devxspace), 5 ether);
    //     devxspace.payWithToken(IERC20(devxcoin),seller, 1);
    //     console.log(devxcoin.balanceOf(address(devxspace)));
    //     vm.stopPrank();
    // }

    function testRelease() public {
        testpayWithEth();
        vm.prank(agent);
        devxspace.release(0);
    }

    // function testApproveCancel() public {
    //     testpayWithEth();
    //     // vm.warp(3 days);
    //     vm.prank(buyer);
    //     devxspace.cancel(0);
    //     vm.prank(agent);
    //     escrow.approveCancel(0);
    // }


   function mkaddr(string memory name) public returns (address) {
        address addr = address(
            uint160(uint256(keccak256(abi.encodePacked(name))))
        );
        vm.label(addr, name);
        return addr;
    }
}
