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

function testAcceptTask() public {
    testhire();
    vm.startPrank(seller);
    devxspace.getTasksForBuyer(buyer);
    devxspace.getTasksForSeller(seller);
    devxspace.AcceptTask(1);
    vm.stopPrank();
}



//     function testHireAcceptReject() public {
//         testcreateGig();
//         vm.prank(0x2e767b4A3416Ef16458355EFAcec7d3228Cec08C);
//         devxspace.hire(0);
//         vm.startPrank(0x7a5863fe6A65377A7cd3F2A6d417F489D9DCF353);
//         devxspace.viewOffer(0);
//         devxspace.AcceptOrReject(0, 1);
//         vm.stopPrank();
//     }

//     function testPaymentWithETH() public {
//         testHireAcceptReject();
//         vm.prank(0x2e767b4A3416Ef16458355EFAcec7d3228Cec08C);
//         vm.deal(0x2e767b4A3416Ef16458355EFAcec7d3228Cec08C, 50 ether);
//         devxspace.payWithEth{value: 1 ether}(0x7a5863fe6A65377A7cd3F2A6d417F489D9DCF353, 0);
//     }

//     // function testPaymentWithToken() public {
//     //     testHireAcceptReject();
//     //     vm.startPrank(0x2e767b4A3416Ef16458355EFAcec7d3228Cec08C);
//     //     devxcoin.approve(address(devxspace), 5 ether);
//     //     devxspace.payWithToken(IERC20(devxcoin),0x7a5863fe6A65377A7cd3F2A6d417F489D9DCF353, 0);
//     //     console.log(devxcoin.balanceOf(address(devxspace)));
//     //     vm.stopPrank();
//     // }

//     // function testRelease() public {
//     //     testPaymentWithETH();
//     //     vm.prank(0x9B69F998b2a2b20FF54a575Bd5fB90A5D71656C1);
//     //     escrow.release(0);
//     // }

//     function testApproveCancel() public {
//         testPaymentWithETH();
//         vm.warp(3 days);
//         vm.prank(0x2e767b4A3416Ef16458355EFAcec7d3228Cec08C);
//         devxspace.approveCancel(0);
//         vm.prank(0x7a5863fe6A65377A7cd3F2A6d417F489D9DCF353);
//         escrow.approveCancel(0);
//         vm.prank(0x9B69F998b2a2b20FF54a575Bd5fB90A5D71656C1);
//         escrow.approveCancel(0);
//     }

//     function testCancel() public {
//         testApproveCancel();
//         vm.prank(0x2e767b4A3416Ef16458355EFAcec7d3228Cec08C);
//         devxspace.buyerCancel(0);
//     }


   function mkaddr(string memory name) public returns (address) {
        address addr = address(
            uint160(uint256(keccak256(abi.encodePacked(name))))
        );
        vm.label(addr, name);
        return addr;
    }
}
