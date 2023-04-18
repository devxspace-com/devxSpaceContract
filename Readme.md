## DXCOIN Contract

-  https://sepolia.etherscan.io/address/0x251f12eb6e4e2b5892701273017dee380a81c74e

## DevxSpace Contract

-  https://sepolia.etherscan.io/address/0x3d265c9942ceb2a0cbc1bfa0ad4a2cffc12f1f7d
<br><br>
<br><br>
<br><br>


# **Contract Documentation**
## EscrowByAgentV2
The EscrowByAgentV2 contract is a Solidity smart contract that implements an escrow system where the funds are held by an agent until the recipient confirms the delivery of the goods or services. The contract is based on the IEscrowByAgent interface and inherits the ReentrancyGuard and Ownable contracts from the OpenZeppelin library.
<br>
- SPDX License Identifier
``` solidity

// SPDX-License-Identifier: MIT
Pragma
The contract uses Solidity version 0.8.0 or later:
```

``` solidity
pragma solidity ^0.8.0;

```
## Libraries <br>
The following libraries are imported:

- ReentrancyGuard.sol from the OpenZeppelin library, which provides protection against reentrancy attacks.
- Ownable.sol from the OpenZeppelin library, which provides a onlyOwner modifier to restrict access to certain functions to the contract owner.
- IERC20.sol from the OpenZeppelin library, which provides an interface for the ERC20 token standard.
<br>
``` solidity
import "lib/openzeppelin-contracts/contracts/security/ReentrancyGuard.sol";
import "lib/openzeppelin-contracts/contracts/access/Ownable.sol";
import "lib/openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";

```
## Interface <br>
The contract implements the IEscrowByAgent interface:
``` solidity
import "src/interface.sol/Iescrow.sol";

contract EscrowByAgentV2 is Ownable, ReentrancyGuard, IEscrowByAgent {
```
## Structs <br>
### Pool:
The Pool struct stores the details of a particular escrow
it contains the following:
- **token:** the address of the ERC20 token being held in escrow. If the address is 0x0, it represents ETH.
- **sender:** the address of the sender who initiated the escrow deposit.
- **recipient:** the address of the recipient who will receive the funds once the escrow is released.
- **agent:** the address of the agent who is holding the funds in escrow.
- **createdAt:** the timestamp when the escrow was created.
- **isReleased:** a boolean flag indicating whether the escrow has been released or not.
- **amount:** the amount of tokens or ETH being held in escrow.
```solidity
struct Pool {
    address token;
    address sender;
    address recipient;
    address agent;
    uint64 createdAt;
    bool isReleased;
    uint256 amount;
}
```
### RefundStatus
The RefundStatus struct stores the refund status of a particular escrow pool:

- **sender:** a boolean flag indicating whether the sender has been refunded or not.
- **recipient:** a boolean flag indicating whether the recipient has been refunded or not.
- **agent:** a boolean flag indicating whether the agent has been refunded or not.

```solidity
struct RefundStatus {
    bool sender;
    bool recipient;
    bool agent;
}
```
## State Variables
**The contract has the following state variables:**

- **poolCount:** the total number of escrow pools created so far.
- **feePercent:** the percentage of the escrow amount that will be charged as a fee.
- **agentFeePercent:** the percentage of the escrow amount that will be charged as an agent fee.
- **cancelLockTime:** the number of days after which the sender can cancel the escrow.
- **pools:** a mapping of Pool structs to pool IDs.
- **refundStatusList:** a mapping of RefundStatus structs to pool IDs.
```solidity
    uint256 public poolCount;
    uint96 public immutable feePercent;
    uint96 public immutable agentFeePercent;
    uint64 public immutable cancelLockTime;
    mapping(uint256 => Pool) public pools;
    mapping(uint256 => RefundStatus) public refundStatusList;
```