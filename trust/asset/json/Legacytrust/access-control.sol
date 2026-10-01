interface IAccessPredicate {
    function hasAccess(uint256 toolId, address account, bytes calldata data) external view returns (bool);
    function name() external view returns (string memory);
}
